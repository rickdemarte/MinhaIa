import sys
from utils.handlers import ResponseHandler as handler


class MessageProcessor:
    """Handles message processing and file integration"""
    
    @staticmethod
    def process_message_with_files(args) -> str:
        """Process base message and integrate file contents"""
        mensagem = args.mensagem
        
        # Process code file
        if args.codigo:
            codigo = handler.processar_arquivo_codigo(args.codigo)
            mensagem = f"{mensagem}\n\n### Código fornecido:\n{codigo}"
        
        # Process text file
        if args.texto:
            mensagem = f"{mensagem}\n{handler.processar_arquivo_codigo(args.texto)}"
        
        # Process PDF file
        if args.pdf:
            pdf_content = handler.processar_arquivo_pdf(args.pdf)
            mensagem = f"{mensagem}\n\n### Conteúdo do PDF:\n{pdf_content}"
        
        return mensagem
    
    @staticmethod
    def handle_transcription(args, provider_name: str, config_manager):
        """Handle audio transcription requests"""
        if not args.transcribe:
            return None
            
        from providers.AWStranscribe_provider import AWSTranscribeProvider
        
        audiofile = args.transcribe
        media_format = audiofile.split('.')[-1].lower()
        print(f"Transcrevendo áudio: {audiofile} (formato: {media_format})", file=sys.stderr)
        
        if provider_name != 'whisper':
            try:
                provider = AWSTranscribeProvider()
                bucket_name = config_manager.get_transcription_bucket()
                response = provider.call_api(
                    audiofile, 
                    language_code="pt-BR", 
                    media_format=media_format,
                    bucket_name=bucket_name
                )
                print(f"Transcrição concluída\n")
                handler.process_response(response, args)
                sys.exit(0)
            except Exception as e:
                print(f"Erro ao transcrever áudio:\nErro: {e}", file=sys.stderr)
                sys.exit(1)
        
        return None
    
    @staticmethod
    def validate_message(mensagem: str, args) -> str:
        """Validate and prepare final message"""
        if not mensagem.strip():
            if args.provider == 'whisper':
                return "Transcreva esse áudio em português"
            else:
                print("Erro: Nenhuma mensagem fornecida", file=sys.stderr)
                sys.exit(1)
        return mensagem
