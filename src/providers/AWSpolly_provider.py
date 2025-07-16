import os
import sys
import re
import boto3

from pathlib import Path

from botocore.exceptions import ClientError, NoCredentialsError
from .base import BaseProvider
from constants import (
    DEFAULT_VOICE_ID,
    DEFAULT_ENGINE,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_LANGUAGE_CODE,
    VOICE_MAPPING
)


class AWSPollyProvider(BaseProvider):
    """Classe para gerar áudio usando AWS Polly."""


    def __init__(self):
        self.polly = self.inicializar_cliente_polly()

    def inicializar_cliente_polly(self):
        """Inicializa e retorna o cliente AWS Polly"""
        try:
            # Tenta criar o cliente com as credenciais configuradas
            polly_client = boto3.client('polly', region_name='us-west-2')
            
            # Testa se as credenciais estão funcionando
            polly_client.describe_voices(LanguageCode='pt-BR')
            
            return polly_client
        except NoCredentialsError:
            print("Erro: Credenciais AWS não encontradas", file=sys.stderr)
            print("Configure as credenciais usando:", file=sys.stderr)
            print("  - aws configure", file=sys.stderr)
            print("  - Variáveis de ambiente AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY", file=sys.stderr)
            print("  - Arquivo ~/.aws/credentials", file=sys.stderr)
            sys.exit(1)
        except ClientError as e:
            print(f"Erro ao conectar com AWS Polly: {e}", file=sys.stderr)
            sys.exit(1)
    


    def limpar_texto_para_audio(self,texto):
        """Remove caracteres desnecessários e formata texto para TTS"""
        # Remove múltiplas quebras de linha
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        
        # Remove espaços no início e fim das linhas
        texto = '\n'.join(line.strip() for line in texto.split('\n'))
        
        # Remove marcações markdown comuns
        # Headers
        texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
        
        # Bold e itálico
        texto = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', texto)  # Bold + itálico
        texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)      # Bold
        texto = re.sub(r'\*(.*?)\*', r'\1', texto)          # Itálico
        texto = re.sub(r'__(.*?)__', r'\1', texto)          # Bold alternativo
        texto = re.sub(r'_(.*?)_', r'\1', texto)            # Itálico alternativo
        
        # Remove código inline e blocos de código
        texto = re.sub(r'```[^`]*```', '', texto, flags=re.DOTALL)
        texto = re.sub(r'`([^`]+)`', r'\1', texto)
        
        # Remove links mas mantém o texto
        texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)
        
        # Remove URLs
        texto = re.sub(r'https?://\S+', '', texto)
        
        # Remove caracteres especiais de markdown
        texto = re.sub(r'^[\*\-\+]\s+', '', texto, flags=re.MULTILINE)  # Listas
        texto = re.sub(r'^\d+\.\s+', '', texto, flags=re.MULTILINE)     # Listas numeradas
        texto = re.sub(r'^>\s+', '', texto, flags=re.MULTILINE)         # Citações
        texto = re.sub(r'\|', ' ', texto)                               # Tabelas
        
        # Remove emojis e caracteres especiais
        texto = re.sub(r'[^\w\s\.,;:!?\-áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]', ' ', texto)
        
        # Remove múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remove espaços antes de pontuação
        texto = re.sub(r'\s+([.,;:!?])', r'\1', texto)
        
        # Garante espaço após pontuação
        texto = re.sub(r'([.,;:!?])(\w)', r'\1 \2', texto)
        
        # Remove linhas vazias excessivas
        texto = re.sub(r'\n\s*\n', '\n', texto)
        
        return texto.strip()

    def dividir_texto_inteligente(self,texto, limite=2900):
        """
        Divide o texto em partes menores de forma inteligente,
        tentando não quebrar frases no meio.
        AWS Polly tem limite de 3000 caracteres para neural engine.
        """
        if len(texto) <= limite:
            return [texto]
        
        partes = []
        texto_restante = texto
        
        while texto_restante:
            if len(texto_restante) <= limite:
                partes.append(texto_restante)
                break
            
            # Encontra um ponto de corte adequado
            corte = limite
            
            # Tenta cortar em um parágrafo (duas quebras de linha)
            pos_paragrafo = texto_restante.rfind('\n\n', 0, limite)
            if pos_paragrafo > limite * 0.7:  # Se encontrou um parágrafo após 70% do limite
                corte = pos_paragrafo
            else:
                # Tenta cortar em uma quebra de linha simples
                pos_linha = texto_restante.rfind('\n', 0, limite)
                if pos_linha > limite * 0.7:
                    corte = pos_linha
                else:
                    # Tenta cortar em uma frase (ponto final)
                    pos_frase = max(
                        texto_restante.rfind('. ', 0, limite),
                        texto_restante.rfind('! ', 0, limite),
                        texto_restante.rfind('? ', 0, limite)
                    )
                    if pos_frase > limite * 0.7:
                        corte = pos_frase + 1  # Inclui o ponto
                    else:
                        # Tenta cortar em vírgula ou ponto e vírgula
                        pos_virgula = max(
                            texto_restante.rfind(', ', 0, limite),
                            texto_restante.rfind('; ', 0, limite)
                        )
                        if pos_virgula > limite * 0.7:
                            corte = pos_virgula + 1
                        else:
                            # Último recurso: corta em espaço
                            pos_espaco = texto_restante.rfind(' ', 0, limite)
                            if pos_espaco > 0:
                                corte = pos_espaco
            
            # Adiciona a parte e continua com o resto
            partes.append(texto_restante[:corte].strip())
            texto_restante = texto_restante[corte:].strip()
        
        return partes

    def concatenar_audios(self, arquivos_audio, arquivo_saida):
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
            
            return arquivo_saida
            
        except Exception as e:
            print(f"[✗] Erro ao concatenar áudios: {e}", file=sys.stderr)
            return False

    def criar_ssml_texto(self,texto):
        """
        Cria texto SSML para melhor controle da síntese de voz
        """
        # Escapa caracteres especiais do XML
        texto = texto.replace('&', '&amp;')
        texto = texto.replace('<', '&lt;')
        texto = texto.replace('>', '&gt;')
        texto = texto.replace('"', '&quot;')
        texto = texto.replace("'", '&apos;')
        
        # Adiciona pausas após pontuação
        texto = texto.replace('.', '.<break time="500ms"/>')
        texto = texto.replace('!', '!<break time="500ms"/>')
        texto = texto.replace('?', '?<break time="500ms"/>')
        texto = texto.replace(',', ',<break time="200ms"/>')
        texto = texto.replace(';', ';<break time="300ms"/>')
        texto = texto.replace(':', ':<break time="300ms"/>')
        
        # Adiciona pausa maior entre parágrafos
        texto = texto.replace('\n\n', '<break time="1s"/>')
        texto = texto.replace('\n', '<break time="700ms"/>')
        
        return f'<speak>{texto}</speak>'

    def call_api(self,texto, nome_arquivo="voz.mp3", voice_id=DEFAULT_VOICE_ID, 
                        engine=DEFAULT_ENGINE, language_code=DEFAULT_LANGUAGE_CODE):
        """Gera arquivo(s) MP3 com a resposta usando AWS Polly"""
        
        # Inicializa o cliente Polly
        #polly_client = self.polly
        
        # Limpa o texto antes de processar
        texto_limpo = self.limpar_texto_para_audio(texto)
        
        if not texto_limpo:
            print("Erro: Texto vazio após limpeza", file=sys.stderr)
            sys.exit(1)
        
        # Divide o texto se necessário
        partes = self.dividir_texto_inteligente(texto_limpo, limite=2900)
        
        if len(partes) == 1:
            # Texto cabe em um único arquivo
            print(f"[📝] Texto preparado para áudio ({len(texto_limpo)} caracteres)", file=sys.stderr)
            self._gerar_audio_parte_polly(texto_limpo, nome_arquivo, voice_id, engine, 
                                    language_code, self.polly)
            return nome_arquivo
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
                
                if self._gerar_audio_parte_polly(parte, str(nome_parte), voice_id, engine, 
                                        language_code, self.polly):
                    arquivos_temporarios.append(str(nome_parte))
                else:
                    # Se falhar, remove arquivos temporários já criados
                    for arquivo in arquivos_temporarios:
                        try:
                            os.remove(arquivo)
                        except:
                            pass
                    sys.exit(1)
            
            # Concatena os arquivos
            print(f"\n[🎵] Processando áudio final...", file=sys.stderr)
            
            if self.concatenar_audios(arquivos_temporarios, nome_arquivo):
                # Cria arquivo de informações
                info_file = diretorio / f"{nome_base}_info.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"Áudio gerado a partir de {len(partes)} partes\n")
                    f.write(f"Arquivo final: {nome_arquivo}\n")
                    f.write(f"Tamanho total do texto: {len(texto_limpo)} caracteres\n")
                    f.write(f"Serviço: AWS Polly\n")
                    f.write(f"Voz: {voice_id}\n")
                    f.write(f"Engine: {engine}\n")
                    f.write(f"Idioma: {language_code}\n")
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
                return False

    def _gerar_audio_parte_polly(self,texto, nome_arquivo, voice_id, engine, 
                                language_code, polly_client):
        """Função auxiliar para gerar uma parte do áudio usando AWS Polly"""
        try:
            # Prepara o texto em formato SSML
            ssml_text = self.criar_ssml_texto(texto)
            
            # Solicita a síntese de voz
            try:
                response = polly_client.synthesize_speech(
                    Text=ssml_text,
                    TextType='ssml',
                    OutputFormat=DEFAULT_OUTPUT_FORMAT,
                    VoiceId=voice_id,
                    Engine=engine,
                    SampleRate=DEFAULT_SAMPLE_RATE,
                    LanguageCode=language_code
                )
            except ClientError as e:
                # Se falhar com neural engine, tenta com standard
                if engine == 'neural' and 'Neural' in str(e):
                    print(f"[⚠️] Engine neural não disponível, usando standard", file=sys.stderr)
                    response = polly_client.synthesize_speech(
                        Text=ssml_text,
                        TextType='ssml',
                        OutputFormat=DEFAULT_OUTPUT_FORMAT,
                        VoiceId=voice_id,
                        Engine='standard',
                        SampleRate=DEFAULT_SAMPLE_RATE
                    )
                else:
                    raise e
            
            # Salva o arquivo de áudio
            with open(nome_arquivo, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            print(f"[✓] Áudio salvo: {nome_arquivo}", file=sys.stderr)
            return nome_arquivo
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'InvalidSsmlException':
                print(f"[✗] Erro de SSML: {error_message}", file=sys.stderr)
                print("[🔄] Tentando sem formatação SSML...", file=sys.stderr)
                
                # Tenta novamente sem SSML
                try:
                    response = polly_client.synthesize_speech(
                        Text=texto,
                        TextType='text',
                        OutputFormat=DEFAULT_OUTPUT_FORMAT,
                        VoiceId=voice_id,
                        Engine=engine,
                        SampleRate=DEFAULT_SAMPLE_RATE,
                        LanguageCode=language_code
                    )
                    
                    with open(nome_arquivo, 'wb') as f:
                        f.write(response['AudioStream'].read())
                    
                    print(f"[✓] Áudio salvo (sem SSML): {nome_arquivo}", file=sys.stderr)
                    return nome_arquivo
                except Exception as e2:
                    print(f"[✗] Erro ao gerar áudio sem SSML: {e2}", file=sys.stderr)
                    return False
            else:
                print(f"[✗] Erro AWS Polly: {error_code} - {error_message}", file=sys.stderr)
                return False
                
        except Exception as e:
            print(f"[✗] Erro ao gerar áudio: {e}", file=sys.stderr)
            return False

    def listar_vozes_disponiveis(self,language_code=None):
        """Lista as vozes disponíveis no AWS Polly"""
        try:
            polly_client = self.inicializar_cliente_polly()
            
            if language_code:
                response = polly_client.describe_voices(LanguageCode=language_code)
            else:
                response = polly_client.describe_voices()
            
            print("\n[🎤] Vozes disponíveis no AWS Polly:")
            
            vozes_por_idioma = {}
            for voice in response['Voices']:
                lang = voice['LanguageCode']
                if lang not in vozes_por_idioma:
                    vozes_por_idioma[lang] = []
                vozes_por_idioma[lang].append(voice)
            
            for lang in sorted(vozes_por_idioma.keys()):
                print(f"\n{lang}:")
                for voice in vozes_por_idioma[lang]:
                    engines = ', '.join(voice['SupportedEngines'])
                    print(f"  - {voice['Id']} ({voice['Gender']}) - Engines: {engines}")
                    
        except Exception as e:
            print(f"Erro ao listar vozes: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return VOICE_MAPPING