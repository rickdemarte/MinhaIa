import os
import sys
import re

from pathlib import Path
from .base import BaseProvider
from utils.error_handler import SecureErrorHandler
from constants import DEFAULT_VOICE, DEFAULT_TTS_MODEL, VOICE_INSTRUCTIONS
from utils.text_utils import limpar_texto_para_audio, dividir_texto_inteligente

class OpenAIAudio(BaseProvider):
    """Classe para manipulação de áudio usando OpenAI TTS"""

    def __init__(self,arquivo):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = None
        self.nome_arquivo=arquivo

    def _initialize_client(self):
        """Inicializa o cliente OpenAI"""
        if not self.api_key:
            raise Exception("Erro: Variável de ambiente OPENAI_API_KEY não encontrada")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("Erro: Biblioteca 'openai' não instalada. Execute: pip install openai")


    def concatenar_audios(self,arquivos_audio, arquivo_saida):
        """Concatena múltiplos arquivos de áudio em um único arquivo"""
        try:
            from pydub import AudioSegment
        except ImportError:
            print("Erro: Funcionalidade de concatenação requer biblioteca pydub", file=sys.stderr)
            print("Instale com: pip install pydub", file=sys.stderr)
            return False
        
        try:
            print(f"[🔗] Concatenando {len(arquivos_audio)} arquivos de áudio...", file=sys.stderr)
            
            # Carrega o primeiro arquivo
            audio_combinado = AudioSegment.from_mp3(arquivos_audio[0])
            
            # Adiciona os demais arquivos
            for i, arquivo in enumerate(arquivos_audio[1:], 2):
                print(f"    - Adicionando parte {i}/{len(arquivos_audio)}", file=sys.stderr)
                audio_parte = AudioSegment.from_mp3(arquivo)
                # Adiciona um pequeno silêncio entre as partes (500ms)
                silencio = AudioSegment.silent(duration=500)
                audio_combinado = audio_combinado + silencio + audio_parte
            
            # Exporta o arquivo combinado
            audio_combinado.export(arquivo_saida, format="mp3")
            print(f"[✓] Áudio combinado salvo: {arquivo_saida}", file=sys.stderr)
            
            # Remove os arquivos temporários
            print("[🗑️] Removendo arquivos temporários...", file=sys.stderr)
            for arquivo in arquivos_audio:
                try:
                    os.remove(arquivo)
                    print(f"    - Removido: {arquivo}", file=sys.stderr)
                except Exception as e:
                    print(f"    - Erro ao remover {arquivo}: {e}", file=sys.stderr)
            
            return True
            
        except Exception as e:
            print(f"[✗] Erro ao concatenar áudios: {e}", file=sys.stderr)
            return False

    def call_api(self, texto, nome_arquivo="voz.mp3", modelo=DEFAULT_TTS_MODEL, voz=DEFAULT_VOICE, persona=VOICE_INSTRUCTIONS):
        """Gera arquivo(s) MP3 com a resposta usando TTS da OpenAI"""
        
        if not self.client:
            self._initialize_client()
        
        # Limpa o texto antes de processar
        texto_limpo = limpar_texto_para_audio(texto)
        
        if not texto_limpo:
            raise Exception("Erro: Texto vazio após limpeza")
        
        # Divide o texto se necessário
        partes = dividir_texto_inteligente(texto_limpo, 3500)
        
        if len(partes) == 1:
            # Texto cabe em um único arquivo
            print(f"[📝] Texto preparado para áudio ({len(texto_limpo)} caracteres)", file=sys.stderr)
            file_path = self._gerar_audio_parte(texto_limpo, nome_arquivo, modelo, voz, extensao='.mp3', persona=VOICE_INSTRUCTIONS)
            return file_path
        else:
            # Texto precisa ser dividido
            print(f"[📝] Texto muito grande ({len(texto_limpo)} caracteres)", file=sys.stderr)
            print(f"[✂️] Dividindo em {len(partes)} partes", file=sys.stderr)
            
            # Extrai nome base e extensão
            path = Path(nome_arquivo)
            nome_base = path.stem
            extensao = path.suffix or '.mp3'
            diretorio = path.parent
            
            arquivos_temporarios = []
            
            for i, parte in enumerate(partes, 1):
                nome_parte = diretorio / f"{nome_base}_parte{i}_temp{extensao}"
                print(f"\n[🎯] Gerando parte {i}/{len(partes)} ({len(parte)} caracteres)", file=sys.stderr)

                if self._gerar_audio_parte(parte, str(nome_parte), modelo, voz, extensao.lstrip('.').lower(), persona):
                    arquivos_temporarios.append(str(nome_parte))
                else:
                    # Se falhar, remove arquivos temporários já criados
                    for arquivo in arquivos_temporarios:
                        try:
                            os.remove(arquivo)
                        except:
                            pass
                    raise Exception("Erro ao gerar áudio")
            
            # Concatena os arquivos
            print(f"\n[🎵] Processando áudio final...", file=sys.stderr)
            
            if self.concatenar_audios(arquivos_temporarios, nome_arquivo):
                # Cria arquivo de informações
                info_file = diretorio / f"{nome_base}_info.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"Áudio gerado a partir de {len(partes)} partes\n")
                    f.write(f"Arquivo final: {nome_arquivo}\n")
                    f.write(f"Tamanho total do texto: {len(texto_limpo)} caracteres\n")
                    f.write(f"Modelo: {modelo}\n")
                    f.write(f"Voz: {voz}\n")
                    f.write(f"Gerado em: {os.path.basename(sys.argv[0])}\n")

                print(f"[📄] Informações salvas em: {info_file}", file=sys.stderr)
                print(f"\n[✅] Áudio completo gerado com sucesso!", file=sys.stderr)
                return nome_arquivo
            else:
                print(f"\n[⚠️] Não foi possível concatenar os áudios.", file=sys.stderr)
                print(f"[📁] Os arquivos parciais foram mantidos:", file=sys.stderr)
                for arquivo in arquivos_temporarios:
                    if os.path.exists(arquivo):
                        print(f"    - {arquivo}", file=sys.stderr)

    def _gerar_audio_parte(self, texto, nome_arquivo, modelo, voz, extensao, persona):
        """Função auxiliar para gerar uma parte do áudio"""
        try:

            client = self.client

            response = client.audio.speech.create(
                model=modelo,
                voice=voz,
                input=texto
            )
            with open(nome_arquivo, "wb") as f:
                f.write(response.content)
            print(f"[✓] Áudio salvo: {nome_arquivo}", file=sys.stderr)
            return nome_arquivo
        except Exception as e:
            print(f"[✗] Erro ao gerar áudio: {e}", file=sys.stderr)
            return False
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["gpt-4o-audio-preview", "gpt-4o-mini-audio-preview", "tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
