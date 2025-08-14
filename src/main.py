import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from providers.factory import ProviderFactory
from config.manager import ConfigManager
from processors.message_processor import MessageProcessor
from utils.argumentos import CLIArgumentParser
from utils.handlers import ResponseHandler as handler
from API import start_text_api


class AIController:
    """Main controller for AI CLI operations"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.message_processor = MessageProcessor()
        self.provider_factory = ProviderFactory()
    
    def handle_list_models(self, args):
        """Handle --list-models command"""
        if args.list_models:
            self.config_manager.list_available_models()
            sys.exit(0)
    
    def process_api_call(self, args, provider_name: str, mensagem: str, modelo: str, max_tokens: int, is_o_model: bool):
        """Process API call based on provider and arguments"""
        print(f"Enviando para {provider_name.upper()}...", file=sys.stderr)
        if is_o_model:
            print("Aviso: Modelos O podem levar mais tempo para processar respostas complexas", file=sys.stderr)
        
        # Handle special cases
        if provider_name == 'whisper':
            provider = self.provider_factory.create_provider('whisper')
            return provider.call_api(args.transcribe, mensagem, modelo, max_tokens, persona=args.persona)
        elif provider_name == 'dryrun' and mensagem != '':
            return mensagem
        elif provider_name == 'openai':
            provider = self.provider_factory.create_provider('openai')
            return provider.call_api(
                mensagem,
                modelo,
                max_tokens,
                is_o_model=is_o_model,
                persona=args.persona,
                persistent=getattr(args, 'persistent', None)
            )
        elif provider_name == 'assistant':
            provider = self.provider_factory.create_provider('assistant')
            return provider.call_api(mensagem, modelo, max_tokens, persona=args.persona,is_o_model=is_o_model, files=args.arquivos)
        else:
            # Handle other providers
            provider = self.provider_factory.create_provider(provider_name)
            return provider.call_api(mensagem, modelo, max_tokens, persona=args.persona)
    
    def run(self, args):
        """Main execution method"""
        # Handle list models command
        self.handle_list_models(args)
        
        # Handle transcription if requested
        self.message_processor.handle_transcription(args, args.provider, self.config_manager)
        
        # Process message with files
        mensagem = self.message_processor.process_message_with_files(args)
        
        # Validate message
        mensagem = self.message_processor.validate_message(mensagem, args)
        
        # Get model configuration
        modelo, max_tokens, is_o_model = self.config_manager.get_model_config(args, args.provider)
        
        # Override max_tokens if specified
        if args.max_tokens:
            max_tokens = args.max_tokens
        
        # Process API call
        response = self.process_api_call(args, args.provider, mensagem, modelo, max_tokens, is_o_model)
        
        # Process response
        handler.process_response(response, args)


def main():
    """Main entry point for the AI CLI ou API"""
    import argparse
    parser = argparse.ArgumentParser(
            description="Cliente unificado para APIs de IA",
            formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--online', action='store_true', help='Inicia a API FastAPI')
    parser.add_argument('--host', type=str, help='Host para a API (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, help='Porta para a API (default: 8000)')
    parser.add_argument('--secure', action='store_true', help='Usa chaves de API para autenticação')
    args, _ = parser.parse_known_args()

    if args.online:
        start_text_api(args.host or '0.0.0.0', args.port or 8000)
    else:
        # CLI tradicional
        cli_parser = CLIArgumentParser()
        args = cli_parser.parse_args()
        controller = AIController()
        controller.run(args)

if __name__ == "__main__":
    main()