import os
import sys
import re
from pathlib import Path

from .base import BaseProvider
from constants import VOICE_INSTRUCTIONS
from utils.text_utils import limpar_texto_para_audio, dividir_texto_inteligente

class GroqProviderTTS(BaseProvider):
    """Classe para manipulação de áudio usando GROQ TTS"""

    def __init__(self):
        super().__init__(api_key=os.getenv('GROQ_API_KEY'))
        self.client = None
        
    def _initialize_client(self):
        """Inicializa o cliente GROQ"""
        if not self.api_key:
            raise Exception("Erro: Variável de ambiente GROQ_API_KEY não encontrada")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("Erro: Biblioteca 'groq' não instalada. Execute: pip install groq")

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
        
    def call_api(self, texto, nome_arquivo="voz.mp3", modelo="playai-tts", voz="Adelaide-PlayAI", persona=VOICE_INSTRUCTIONS):
        """Gera arquivo(s) MP3 com a resposta usando TTS da GROQ"""
        
        if not self.client:
            self._initialize_client()
        
        texto_limpo = limpar_texto_para_audio(texto)
        
        if not texto_limpo:
            raise Exception("Erro: Texto vazio após limpeza")
        
        partes = dividir_texto_inteligente(texto_limpo, 1200)
        
        if len(partes) == 1:
            self._gerar_audio_parte(texto_limpo, nome_arquivo, modelo, voz, persona)
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

                #self, texto, nome_arquivo, modelo, extensao, voz, persona
                if self._gerar_audio_parte(parte, str(nome_parte), modelo, extensao.lstrip('.').lower(), voz):
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
            else:
                print(f"\n[⚠️] Não foi possível concatenar os áudios.", file=sys.stderr)
                print(f"[📁] Os arquivos parciais foram mantidos:", file=sys.stderr)
                for arquivo in arquivos_temporarios:
                    if os.path.exists(arquivo):
                        print(f"    - {arquivo}", file=sys.stderr)
    
    def _gerar_audio_parte(self, texto, nome_arquivo, modelo, extensao, voz):
        """Função auxiliar para gerar uma parte do áudio"""
        try:
            client = self.client

            response = client.audio.speech.create(
                model=modelo,
                voice=voz,
                response_format=extensao,
                input=texto
            )
            if response:
                response.write_to_file(nome_arquivo)
            print(f"[✓] Áudio salvo: {nome_arquivo}", file=sys.stderr)
            return nome_arquivo
        except Exception as e:
            print(f"[✗] Erro ao gerar áudio: {e}", file=sys.stderr)
            return False

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["playai-tts"]
