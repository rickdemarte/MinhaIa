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
from utils.formatters import remove_markdown, format_as_log
from utils.file_handlers import processar_arquivo_codigo, processar_arquivo_pdf
from utils.audio import gerar_audio_openai

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
    provider_models = models_config[provider]['models']
    
    if args.fast and 'fast' in provider_models:
        config = provider_models['fast']
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
    if args.voz:
        print(remove_markdown(response))
        gerar_audio_openai(response, args.voz)
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

def main():
    # Carrega configuração dos modelos
    models_config = load_models_config()
    
    parser = argparse.ArgumentParser(
        description="Cliente unificado para APIs de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumentos
    parser.add_argument('mensagem', nargs='?', default='', help='Texto para enviar')
    parser.add_argument('--provider', choices=['openai', 'claude', 'deepseek','qwen'], default='openai')
    parser.add_argument('--claude', action='store_true', help='Usa API da Anthropic')
    parser.add_argument('--deepseek', action='store_true', help='Usa API da DeepSeek')
    parser.add_argument('--qwen', action='store_true', help='Usa API da Alibaba')
    parser.add_argument('-t', action='store_true', help='Remove markdown')
    parser.add_argument('-f', type=str, help='Salva em arquivo')
    parser.add_argument('-p', action='store_true', help='Formato log')
    parser.add_argument('--voz', type=str, nargs='?', const='voz.mp3')
    
    # Modelos
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument('--fast', action='store_true')
    model_group.add_argument('--smart', action='store_true')
    model_group.add_argument('--smartest', action='store_true')
    model_group.add_argument('--absurdo', action='store_true')
    model_group.add_argument('--model', type=str)
    
    # Arquivos
    parser.add_argument('--codigo', type=str)
    parser.add_argument('--pdf', type=str)
    
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
    
    # Validações

    if args.claude:
        args.provider = 'claude'

    if args.deepseek:
        args.provider = 'deepseek'

    if args.qwen:
        args.provider = 'qwen'

    if args.absurdo and args.provider != 'openai':
        print("Erro: --absurdo disponível apenas para OpenAI", file=sys.stderr)
        sys.exit(1)
    
    if args.voz and args.provider != 'openai':
        print("Erro: --voz disponível apenas para OpenAI", file=sys.stderr)
        sys.exit(1)
    
    # Processa mensagem
    mensagem = args.mensagem
    
    if args.codigo:
        codigo = processar_arquivo_codigo(args.codigo)
        mensagem = f"{mensagem}\n\n### Código fornecido:\n{codigo}"
    
    if args.pdf:
        pdf_content = processar_arquivo_pdf(args.pdf)
        mensagem = f"{mensagem}\n\n### Conteúdo do PDF:\n{pdf_content}"
    
    if not mensagem.strip():
        print("Erro: Nenhuma mensagem fornecida", file=sys.stderr)
        sys.exit(1)
    
    # Configuração do modelo
    modelo, max_tokens, is_o_model = get_model_config(args, args.provider, models_config)
    
    if args.max_tokens:
        max_tokens = args.max_tokens
    
    # Chama API
    print(f"Enviando para {args.provider.upper()}...", file=sys.stderr)
    
    if args.provider == 'deepseek':
        provider = DeepSeekProvider()
        response = provider.call_api(mensagem, modelo, max_tokens)
    elif args.provider == 'claude':
        provider = ClaudeProvider()
        response = provider.call_api(mensagem, modelo, max_tokens)
    elif args.provider == 'qwen':
        provider = Qwen3Provider()
        response = provider.call_api(mensagem, modelo, max_tokens)
    else:
        provider = OpenAIProvider()
        response = provider.call_api(mensagem, modelo, max_tokens, is_o_model=is_o_model)
    
    # Processa resposta
    process_response(response, args)

if __name__ == "__main__":
    main()