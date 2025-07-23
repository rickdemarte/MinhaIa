import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

class ClaudeProvider(BaseProvider):
    """Provider para Anthropic Claude API usando LangChain"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = None
        self.max_tokens = None
    
    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo Claude LangChain"""
        if not self.api_key:
            print("Erro: Variável de ambiente ANTHROPIC_API_KEY não encontrada", file=sys.stderr)
            print("Execute: export ANTHROPIC_API_KEY='sua_chave_aqui'", file=sys.stderr)
            sys.exit(1)
        
        try:
            return ChatAnthropic(
                api_key=self.api_key,
                model=self.model or "claude-3-5-sonnet-20241022",
                max_tokens=self.max_tokens or 2000,
                temperature=0.7
            )
        except ImportError:
            print("Erro: Biblioteca 'langchain-anthropic' não instalada. Execute: pip install langchain-anthropic", file=sys.stderr)
            sys.exit(1)
    
    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do Claude usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens
        
        try:
            print(f"Usando modelo Claude: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            return super().call_api(message, model, max_tokens, **kwargs)
            
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