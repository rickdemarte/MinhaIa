import json
import os
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from providers.openai_provider import OpenAIProvider
from providers.claude_provider import ClaudeProvider
from providers.deepseek_provider import DeepSeekProvider
from providers.alibaba_provider import Qwen3Provider
from providers.grok_provider import GrokProvider
from providers.openaiWhisper_provider import WhisperProvider
from providers.AWStranscribe_provider import AWSTranscribeProvider

from utils.argumentos import CLIArgumentParser
from utils.handlers import ResponseHandler as handler


def load_models_config():
    """Carrega configuração dos modelos do arquivo JSON"""
    config_path = Path(__file__).parent.parent / "config" / "models.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração não encontrado: {config_path}", file=sys.stderr)
        sys.exit(1)

def get_model_config(args, provider, models_config):
    """Determina qual modelo usar baseado nos argumentos"""
    print(f"Usando provider: {provider}", file=sys.stderr)
    provider_models = models_config[provider]['models']
    
    # Verifica se o provider tem modelos configurados
    if args.transcribe and provider not in ['openai', 'whisper']:
        return provider_models['transcribe']['bucket_name']
    elif args.fast and 'fast' in provider_models:
        config = provider_models['fast']
    elif args.cheap and 'cheap' in provider_models:
        config = provider_models['cheap']
    elif args.smart and 'smart' in provider_models:
        config = provider_models['smart']
    elif args.smartest and 'smartest' in provider_models:
        config = provider_models['smartest']
    elif args.absurdo and provider == 'openai' and 'absurdo' in provider_models:
        config = provider_models['absurdo']
    elif args.model:
        # Modelo customizado
        return args.model, 4096, False
    else:
        config = provider_models['default']
    
    return config['model'], config['max_tokens'], config.get('is_o_model', False)

def main():
    # Carrega configuração dos modelos
    models_config = load_models_config()
    
    # Parse argumentos usando a classe abstrata
    cli_parser = CLIArgumentParser()
    args = cli_parser.parse_args()
    
    # Lista modelos
    if args.list_models:
        print("\n=== Modelos Disponíveis ===")
        for provider, config in models_config.items():
            print(f"\n{provider.upper()}:")
            for alias, model_config in config['models'].items():
                print(f"  {alias}: {model_config['model']} ({model_config['description']})")
        sys.exit(0)
    
    mensagem = args.mensagem
    
    if args.codigo:
        codigo = handler.processar_arquivo_codigo(args.codigo)
        mensagem = f"{mensagem}\n\n### Código fornecido:\n{codigo}"
    
    if args.texto:
        mensagem = f"{mensagem}\n{handler.processar_arquivo_codigo(args.texto)}"

    if args.pdf:
        pdf_content = handler.processar_arquivo_pdf(args.pdf)
        mensagem = f"{mensagem}\n\n### Conteúdo do PDF:\n{pdf_content}"
    
    # Verifica se o usuário passou um arquivo de áudio para transcrição
    if args.transcribe:
        audiofile = args.transcribe
        media_format = audiofile.split('.')[-1].lower()
        print(f"Transcrevendo áudio: {audiofile} (formato: {media_format})", file=sys.stderr)
        if args.provider != 'whisper':
            try:
                provider = AWSTranscribeProvider()
                response = provider.call_api(audiofile, language_code="pt-BR", media_format=media_format, 
                                           bucket_name=get_model_config(args, args.provider, models_config))
                print(f"Transcrição concluída\n")
                handler.process_response(response, args)
                sys.exit(0)
            except Exception as e:
                print(f"Erro ao transcrever áudio:\nErro: {e}", file=sys.stderr)
                sys.exit(1)
    
    if not mensagem.strip():
        if args.provider == 'whisper':
            mensagem = "Transcreva esse áudio em português"
        else:
            print("Erro: Nenhuma mensagem fornecida", file=sys.stderr)
            sys.exit(1)
    
    # Configuração do modelo
    modelo, max_tokens, is_o_model = get_model_config(args, args.provider, models_config)
    
    if args.max_tokens:
        max_tokens = args.max_tokens
    
    # Chama API
    print(f"Enviando para {args.provider.upper()}...", file=sys.stderr)
    
    if args.provider == 'whisper':
        provider = WhisperProvider()
        response = provider.call_api(audiofile, mensagem, modelo, max_tokens, persona=args.persona)
    elif args.provider == 'deepseek':
        provider = DeepSeekProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=args.persona)
    elif args.provider == 'claude':
        provider = ClaudeProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=args.persona)
    elif args.provider == 'qwen':
        provider = Qwen3Provider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=args.persona)
    elif args.provider == 'grok':
        provider = GrokProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=args.persona)
    elif args.provider == 'dryrun' and mensagem != '':
        response = mensagem
    else:
        provider = OpenAIProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, is_o_model=is_o_model, persona=args.persona)
    
    # Processa resposta
    handler.process_response(response, args)

if __name__ == "__main__":
    main()