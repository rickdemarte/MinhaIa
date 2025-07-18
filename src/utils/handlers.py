import os
import sys

from providers.openaiTTS_provider import OpenAIAudio
from providers.AWSpolly_provider import AWSPollyProvider
from providers.groqTTS_provider import GroqProviderTTS
from utils.formatters import remove_markdown, format_as_log


class ResponseHandler:
    """Classe para tratar a resposta do resultado"""
    
    def processar_arquivo_codigo(arquivo):
        """Lê e processa um arquivo de código"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Erro ao ler o arquivo de código: {e}", file=sys.stderr)
            sys.exit(1)

    def processar_arquivo_pdf(arquivo):
        """Lê e processa um arquivo PDF"""
        try:
            import pdfplumber
        except ImportError:
            print("Erro: Biblioteca 'pdfplumber' não instalada. Execute: pip install pdfplumber", file=sys.stderr)
            sys.exit(1)
        
        try:
            with pdfplumber.open(arquivo) as pdf:
                texto_pdf = ''
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        texto_pdf += page_text + '\n'
            
            if not texto_pdf.strip():
                print(f"Aviso: Nenhum texto extraído de {arquivo}.", file=sys.stderr)
            
            return texto_pdf.strip()
        except Exception as e:
            print(f"Erro ao processar o arquivo PDF '{arquivo}': {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def process_response(response, args):
        """Processa e exibe a resposta conforme os parâmetros"""
        audio_file = None
        if args.voz:
            print(f"Mensagem original: \n {response}", file=sys.stderr)
            if args.provider == 'groq' or args.groq:
                provider = GroqProviderTTS()
                audio_file = provider.call_api(response, args.voz)
            elif args.provider == 'openai':
                provider = OpenAIAudio()
                audio_file = provider.call_api(response, args.voz)
            elif args.provider == 'aws':
                provider = AWSPollyProvider()
                audio_file = provider.call_api(response, args.voz)
            else:
                print(f"Erro: Provedor de voz '{args.provider}' não suportado.", file=sys.stderr)
                sys.exit(1)
        elif args.polly:
            print(remove_markdown(response))
            provider = AWSPollyProvider()
            audio_file = provider.call_api(response, args.polly)
        elif args.t:
            print(remove_markdown(response))
        elif args.f:
            try:
                with open(args.f, 'w', encoding='utf-8') as f:
                    f.write(response)
                print(f"Resposta salva em: {args.f}", file=sys.stderr)
            except IOError as e:
                print(f"Erro ao salvar arquivo: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.p:
            provider_log = "openai" if args.provider == 'openai' else "claude"
            print(format_as_log(response, provider=provider_log))
        else:
            print(response)
        
        if audio_file and args.ouvir:
            print(f"Reproduzindo áudio: {audio_file}", file=sys.stderr)
            os.system(f"mpg123 {audio_file} > /dev/null 2>&1")