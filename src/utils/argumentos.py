import argparse
import sys


class CLIArgumentParser:
    """Classe para gerenciar os argumentos da linha de comando"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Cria e configura o parser de argumentos"""
        parser = argparse.ArgumentParser(
            description="Cliente unificado para APIs de IA",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Argumento principal
        parser.add_argument('mensagem', nargs='?', default='', help='Texto para enviar')
        
        # Argumentos de configuração de API
        parser.add_argument('--online', action='store_true', help='Inicia a API FastAPI')
        parser.add_argument('--port', type=int, default=8000, help='Porta da API FastAPI')
        parser.add_argument('--host', type=str, default='0.0.0.0', help='Host da API FastAPI')
        parser.add_argument('--secure', action='store_true', help='Usa chaves de API para autenticação')

        # Providers
        parser.add_argument('--provider',
                          choices=['aws', 'openai', 'assistant', 'claude', 'deepseek', 'qwen', 'dryrun', 'grok', 'whisper', 'groq', 'gemini', 'perplexity'],
                          default='groq',
                          help='Escolha o provider da API de chat')
        parser.add_argument('--openai', action='store_true', help='Usa API da OpenAI')
        parser.add_argument('--assistant', action='store_true', help='Usa Assistants API da OpenAI')
        parser.add_argument('--claude', action='store_true', help='Usa API da Anthropic')
        parser.add_argument('--deepseek', action='store_true', help='Usa API da DeepSeek')
        parser.add_argument('--qwen', action='store_true', help='Usa API da Alibaba')
        parser.add_argument('--grok', action='store_true', help='Usa API da Grok')
        parser.add_argument('--groq', action='store_true', help='Usa API da Groq')
        parser.add_argument('--gemini', action='store_true', help='Usa API do Gemini')
        parser.add_argument('--perplexity', action='store_true', help='Usa API da Perplexity')
        parser.add_argument('--dryrun', action='store_true', help='Não usa nenhuma API de chat')
        
        # Formatação de saída
        parser.add_argument('-t', action='store_true', help='Remove markdown')
        parser.add_argument('-f', type=str, help='Salva em arquivo')
        parser.add_argument('-p', action='store_true', help='Formato log')
        
        # Audio e voz
        parser.add_argument('--voz', type=str, nargs='?', const='voz.mp3')
        parser.add_argument('--polly', type=str, nargs='?', const='voz.mp3', 
                          help='Gera áudio usando Amazon Polly')
        parser.add_argument('--transcribe', type=str, help='Transcreve áudio usando AWS Transcribe')
        parser.add_argument('--ouvir', action='store_true', help='Reproduz áudio MP3 gerado')
        
        # Modelos (grupo mutuamente exclusivo)
        model_group = parser.add_mutually_exclusive_group()
        model_group.add_argument('--fast', action='store_true')
        model_group.add_argument('--cheap', action='store_true')
        model_group.add_argument('--smart', action='store_true')
        model_group.add_argument('--smartest', action='store_true')
        model_group.add_argument('--absurdo', action='store_true')
        model_group.add_argument('--model', type=str)
        
        # Arquivos de entrada
        parser.add_argument('--codigo', type=str)
        parser.add_argument('--pdf', type=str)
        parser.add_argument('--texto', type=str)
        parser.add_argument('--arquivos', nargs='+', help='Arquivos para Assistants API')
        
        # Personalidade ou código
        parser.add_argument('--persona', type=str, help='Personalidade a ser usada')
        parser.add_argument('--code', type=str, help='Gerador de código puro, sem explicações')
        
        # Outros
        parser.add_argument('--max-tokens', type=int)
        parser.add_argument('--list-models', action='store_true')
        parser.add_argument('--persistent', choices=['yes', 'no'],
                            help='Mantém histórico de conversas na OpenAI')
        
        return parser
    
    def parse_args(self):
        """Parse e valida os argumentos"""
        args = self.parser.parse_args()
        self._validate_args(args)
        self._process_provider_shortcuts(args)
        self._process_persona(args)
        return args
    
    def _validate_args(self, args):
        """Valida combinações de argumentos"""
        # Validação para transcrição
        if args.transcribe:
            if args.openai:
                args.provider = 'openai'
            if args.provider:
                if args.provider == 'openai':
                    args.provider = 'whisper'
                elif args.provider not in ['openai', 'dryrun']:
                    print(f"Erro: --transcribe só pode ser usado com openai ou sem provider\nVocê forneceu {args.provider}", 
                          file=sys.stderr)
                    sys.exit(1)
            else:
                args.provider = 'aws'
        elif not args.provider:
            args.provider = 'openai'
        
        # Validação para áudio
        if args.polly and args.voz:
            print("Erro: --polly e --voz não podem ser usados juntos", file=sys.stderr)
            sys.exit(1)
        
        # Validação para modelo absurdo
        if args.absurdo and args.provider not in ['openai', 'groq']:
            print("Erro: --absurdo disponível apenas para OpenAI e Groq", file=sys.stderr)
            sys.exit(1)

        # Validação para modo persistente
        if args.persistent and not (args.openai or args.provider == 'openai'):
            print("Erro: --persistent só pode ser usado com --openai", file=sys.stderr)
            sys.exit(1)
    
    def _process_provider_shortcuts(self, args):
        """Processa atalhos de providers"""
        if args.dryrun:
            args.provider = 'dryrun'
        elif args.claude:
            args.provider = 'claude'
        elif args.deepseek:
            args.provider = 'deepseek'
        elif args.qwen:
            args.provider = 'qwen'
        elif args.grok:
            args.provider = 'grok'
        elif args.groq:
            args.provider = 'groq'
        elif args.gemini:
            args.provider = 'gemini'
        elif args.openai:
            args.provider = 'openai'
        elif args.perplexity:
            args.provider = 'perplexity'
        elif args.assistant:
            args.provider = 'assistant'

    
    def _process_persona(self, args):
        """Processa personalidade e código"""
        if args.code:
            if args.code is None:
                print("Erro: Ao usar --code é obrigatório informar a linguagem. Exemplo: --code python", 
                      file=sys.stderr)
                sys.exit(1)
            else:
                args.persona = f"Gerador de código {args.code} puro, sem explicações"
        elif not hasattr(args, 'persona') or args.persona is None:
            args.persona = ""