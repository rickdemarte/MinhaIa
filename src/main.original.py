#!/usr/bin/env python3
"""
Cliente unificado para APIs de IA - Ponto de entrada principal
"""

import argparse
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
from providers.openaiTTS_provider import OpenAIAudio
from providers.AWSpolly_provider import AWSPollyProvider
from providers.AWStranscribe_provider import AWSTranscribeProvider

from utils.formatters import remove_markdown, format_as_log
from utils.file_handlers import processar_arquivo_codigo, processar_arquivo_pdf


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

def process_response(response, args):
    """Processa e exibe a resposta conforme os parâmetros"""
    audio_file = None
    if args.voz:
        print(remove_markdown(response))
        provider = OpenAIAudio()
        audio_file = provider.call_api(response, args.voz)
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

def main():

    # Carrega configuração dos modelos
    models_config = load_models_config()
    
    parser = argparse.ArgumentParser(
        description="Cliente unificado para APIs de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumentos
    parser.add_argument('mensagem', nargs='?', default='', help='Texto para enviar')
    parser.add_argument('--provider', choices=['aws','openai', 'claude', 'deepseek','qwen', 'dryrun','grok','whisper'], help='Escolha o provider da API de chat')
    parser.add_argument('--openai', action='store_true', help='Usa API da OpenAI')
    parser.add_argument('--claude', action='store_true', help='Usa API da Anthropic')
    parser.add_argument('--deepseek', action='store_true', help='Usa API da DeepSeek')
    parser.add_argument('--qwen', action='store_true', help='Usa API da Alibaba')
    parser.add_argument('--grok', action='store_true', help='Usa API da Grok')
    parser.add_argument('--dryrun', action='store_true', help='Não usa nenhuma API de chat')
    parser.add_argument('-t', action='store_true', help='Remove markdown')
    parser.add_argument('-f', type=str, help='Salva em arquivo')
    parser.add_argument('-p', action='store_true', help='Formato log')
    
    # Audio e voz
    parser.add_argument('--voz', type=str, nargs='?', const='voz.mp3')
    parser.add_argument('--polly', type=str, nargs='?', const='voz.mp3', help='Gera áudio usando Amazon Polly')
    parser.add_argument('--transcribe', type=str, help='Transcreve áudio usando AWS Transcribe')
    parser.add_argument('--ouvir', action='store_true', help='Reproduz áudio MP3 gerado')

    # Modelos
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument('--fast', action='store_true')
    model_group.add_argument('--cheap', action='store_true')
    model_group.add_argument('--smart', action='store_true')
    model_group.add_argument('--smartest', action='store_true')
    model_group.add_argument('--absurdo', action='store_true')
    model_group.add_argument('--model', type=str)
    
    # Arquivos
    parser.add_argument('--codigo', type=str)
    parser.add_argument('--pdf', type=str)
    parser.add_argument('--texto', type=str)
    
    # Personalidade ou código
    parser.add_argument('--persona', type=str, help='Personalidade a ser usada')
    parser.add_argument('--code', type=str, help='Gerador de código puro, sem explicações')

    # Outros
    parser.add_argument('--max-tokens', type=int)
    parser.add_argument('--list-models', action='store_true')
    
    args = parser.parse_args()

    # Lista modelos
    if args.list_models:
        print("\n=== Modelos Disponíveis ===")
        for provider, config in models_config.items():
            print(f"\n{provider.upper()}:")
            for alias, model_config in config['models'].items():
                print(f"  {alias}: {model_config['model']} ({model_config['description']})")
        sys.exit(0)
    
    # Validações de providers
    if args.transcribe:
        if args.openai:
            args.provider = 'openai'
        if args.provider:
            if args.provider == 'openai':
                args.provider = 'whisper'
            elif args.provider not in ['openai','dryrun']:
                print(f"Erro: --transcribe só pode ser usado com openai ou sem provider\nVocê forneceu {args.provider}", file=sys.stderr)
                sys.exit(1)
        else:
            args.provider = 'aws'
    elif not args.provider:
        args.provider = 'openai'

    if args.claude:
        args.provider = 'claude'

    if args.deepseek:
        args.provider = 'deepseek'

    if args.qwen:
        args.provider = 'qwen'

    if args.grok:
        args.provider = 'grok'
    
    if args.dryrun:
        args.provider = 'dryrun'

    if args.polly and args.voz:
        print("Erro: --polly e --voz não podem ser usados juntos", file=sys.stderr)
        sys.exit(1)
    
    if args.absurdo and args.provider != 'openai':
        print("Erro: --absurdo disponível apenas para OpenAI", file=sys.stderr)
        sys.exit(1)
    
    # Validações de personalidade e código

    if args.code:
        if args.code == None:
            print("Erro: Ao usar --code é obrigatório informar a linguagem. Exemplo: --code python", file=sys.stderr)
            sys.exit(1)
        else:
            persona = f"Gerador de código {args.code} puro, sem explicações"
    elif args.persona:
        persona = args.persona
    else:
        persona = ""
    
    # Exibe todos os argumentos
    #print(f"Argumentos fornecidos: {args}", file=sys.stderr)

    mensagem = args.mensagem
    
    if args.codigo:
        codigo = processar_arquivo_codigo(args.codigo)
        mensagem = f"{mensagem}\n\n### Código fornecido:\n{codigo}"
    
    if args.texto:
        mensagem = f"{mensagem}\n{processar_arquivo_codigo(args.texto)}"

    if args.pdf:
        pdf_content = processar_arquivo_pdf(args.pdf)
        mensagem = f"{mensagem}\n\n### Conteúdo do PDF:\n{pdf_content}"
    
    # Verifica se o usuário passou um arquivo de áudio para transcrição
    if args.transcribe:
        # verifica se o parâmetro --provider openai ou --openai foi passado
        audiofile = args.transcribe
        media_format = audiofile.split('.')[-1].lower()
        print(f"Transcrevendo áudio: {audiofile} (formato: {media_format})", file=sys.stderr)
        if args.provider != 'whisper':
            try:
                provider = AWSTranscribeProvider()
                response = provider.call_api(audiofile, language_code="pt-BR", media_format=media_format, bucket_name=get_model_config(args, args.provider, models_config))
                print(f"Transcrição concluída\n")
                process_response(response, args)
                sys.exit(0)
            except Exception as e:
                print(f"Erro ao transcrever áudio:\nErro: {e}", file=sys.stderr)
                sys.exit(1)
    #elif args.transcribe and args.provider  'aws':
    
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
        response = provider.call_api(audiofile, mensagem, modelo, max_tokens, persona=persona)
    elif args.provider == 'deepseek':
        provider = DeepSeekProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=persona)
    elif args.provider == 'claude':
        provider = ClaudeProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=persona)
    elif args.provider == 'qwen':
        provider = Qwen3Provider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=persona)
    elif args.provider == 'grok':
        provider = GrokProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, persona=persona)
    elif args.provider == 'dryrun' and mensagem != '':
        response = mensagem
    else:
        provider = OpenAIProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, is_o_model=is_o_model, persona=persona)
    
    # Processa resposta
    process_response(response, args)

if __name__ == "__main__":
    main()