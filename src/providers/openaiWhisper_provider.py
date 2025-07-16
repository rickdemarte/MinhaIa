import os
import sys
import openai
import tempfile
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT

MAX_DURATION_SECONDS = 1450

class WhisperProvider(BaseProvider):
    """Provider para OpenAI Whisper API"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = None
    
    def _initialize_client(self):
        """Inicializa o cliente OpenAI"""
        if not self.api_key:
            print("Erro: Variável de ambiente OPENAI_API_KEY não encontrada", file=sys.stderr)
            sys.exit(1)
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            print("Erro: Biblioteca 'openai' não instalada. Execute: pip install openai", file=sys.stderr)
            sys.exit(1)
    
    def _split_audio(self, audio_file_path):
        """
        Divide o arquivo de áudio em segmentos menores se necessário.
        Melhorado para evitar erros de arquivo corrompido.
        """
        try:
            # Tenta detectar o formato do arquivo automaticamente
            file_info = mediainfo(audio_file_path)
            format_hint = file_info.get('format_name', 'mp3').lower()
            
            # Lista de formatos suportados pelo pydub
            supported_formats = ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'mp4', 'wma', 'aac']
            
            # Se o formato não for reconhecido, tenta alguns formatos comuns
            if format_hint not in supported_formats:
                for fmt in supported_formats:
                    try:
                        audio = AudioSegment.from_file(audio_file_path, format=fmt)
                        print(f"Arquivo de áudio detectado como formato: {fmt}", file=sys.stderr)
                        break
                    except:
                        continue
                else:
                    # Se nenhum formato funcionar, tenta sem especificar formato
                    audio = AudioSegment.from_file(audio_file_path)
            else:
                audio = AudioSegment.from_file(audio_file_path, format=format_hint)
            
        except Exception as e:
            print(f"Erro ao carregar arquivo de áudio: {e}", file=sys.stderr)
            print("Tentando carregar sem especificar formato...", file=sys.stderr)
            try:
                audio = AudioSegment.from_file(audio_file_path)
            except Exception as e2:
                print(f"Erro fatal ao carregar áudio: {e2}", file=sys.stderr)
                sys.exit(1)
        
        segments = []
        total_duration = audio.duration_seconds
        
        if total_duration <= MAX_DURATION_SECONDS:
            return [audio_file_path]
        
        num_chunks = int(total_duration // MAX_DURATION_SECONDS) + (1 if total_duration % MAX_DURATION_SECONDS > 0 else 0)
        print(f"Dividindo arquivo de áudio em {num_chunks} partes", file=sys.stderr)
        
        for i in range(num_chunks):
            start_ms = i * MAX_DURATION_SECONDS * 1000
            end_ms = min((i + 1) * MAX_DURATION_SECONDS * 1000, len(audio))
            
            try:
                chunk = audio[start_ms:end_ms]
                
                # Cria arquivo temporário com extensão .wav
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", prefix=f"chunk_{i}_")
                
                # Exporta com parâmetros específicos para garantir compatibilidade
                chunk.export(
                    temp_file.name, 
                    format="wav",
                    parameters=[
                        "-ar", "16000",  # Taxa de amostragem de 16kHz (recomendada para Whisper)
                        "-ac", "1",      # Mono
                        "-acodec", "pcm_s16le"  # Codec PCM 16-bit
                    ]
                )
                
                # Verifica se o arquivo foi criado corretamente
                if os.path.getsize(temp_file.name) > 0:
                    segments.append(temp_file.name)
                    print(f"Segmento {i+1}/{num_chunks} criado: {temp_file.name}", file=sys.stderr)
                else:
                    print(f"Aviso: Segmento {i+1} está vazio", file=sys.stderr)
                    
            except Exception as e:
                print(f"Erro ao criar segmento {i+1}: {e}", file=sys.stderr)
                # Limpa arquivos temporários já criados em caso de erro
                for seg in segments:
                    if seg != audio_file_path and os.path.exists(seg):
                        os.remove(seg)
                sys.exit(1)
        
        return segments
    
    def call_api(self, audio_file_path, mensagem, modelo, max_tokens, **kwargs):
        if not self.client:
            self._initialize_client()
        
        if not Path(audio_file_path).is_file():
            print(f"Erro: Arquivo de áudio '{audio_file_path}' não encontrado", file=sys.stderr)
            return None
        
        try:
            personalidade = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            print(f"Usando modelo OpenAI: {modelo} - (max_tokens: {max_tokens}) {personalidade}", file=sys.stderr)
            
            segments = self._split_audio(audio_file_path)
            full_response = ""
            
            for idx, segment_path in enumerate(segments):
                try:
                    with open(segment_path, "rb") as audio_file:
                        print(f"Convertendo {segment_path} ({idx+1}/{len(segments)})", file=sys.stderr)
                        
                        # Usa a API correta do cliente OpenAI
                        response = self.client.audio.transcriptions.create(
                            model=modelo,
                            file=audio_file,
                            response_format="text",
                            prompt=mensagem if mensagem else None
                        )
                        
                        # Adiciona a resposta ao texto completo
                        if isinstance(response, str):
                            full_response += response.strip() + " "
                        else:
                            # Se a resposta for um objeto, tenta extrair o texto
                            full_response += str(response).strip() + " "
                        
                except Exception as e:
                    print(f"Erro ao processar segmento {segment_path}: {e}", file=sys.stderr)
                    # Continua com os próximos segmentos em vez de parar
                    continue
                finally:
                    # Remove arquivo temporário se não for o original
                    if segment_path != audio_file_path and os.path.exists(segment_path):
                        try:
                            os.remove(segment_path)
                        except:
                            pass  # Ignora erros ao remover arquivos temporários
            
            return full_response.strip()
            
        except Exception as e:
            print(f"Erro na chamada da API OpenAI: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_available_models(self):
        return ["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"]