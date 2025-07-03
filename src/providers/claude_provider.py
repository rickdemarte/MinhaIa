import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT

class ClaudeProvider(BaseProvider):
    """Provider para Anthropic Claude API"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.client = None
    
    def _initialize_client(self):
        """Inicializa o cliente Anthropic"""
        if not self.api_key:
            print("Erro: Variável de ambiente ANTHROPIC_API_KEY não encontrada", file=sys.stderr)
            print("Execute: export ANTHROPIC_API_KEY='sua_chave_aqui'", file=sys.stderr)
            sys.exit(1)
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            print("Erro: Biblioteca 'anthropic' não instalada. Execute: pip install anthropic", file=sys.stderr)
            sys.exit(1)
    
    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do Claude"""
        if not self.client:
            self._initialize_client()
        
        try:
            print(f"Usando modelo Claude: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=DEFAULT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": message}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Erro na chamada da API Claude: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return [
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514"
        ]