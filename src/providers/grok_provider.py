import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT

class GrokProvider(BaseProvider):
    """Provider para XAI SDK API"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('GROK_API_KEY'))
        self.client = None
        
    def _initialize_client(self):
        """Inicializa o cliente XAI SDK"""
        if not self.api_key:
            print("Erro: Variável de ambiente GROK_API_KEY não encontrada", file=sys.stderr)
            sys.exit(1)
        
        try:
            from xai_sdk import Client as XAIClient
            self.client = XAIClient(
                api_key=self.api_key,
            )
        except ImportError:
            # Se a biblioteca não estiver instalada, informa o usuário e mostra o erro completo
            import traceback
            print("Erro: Biblioteca 'xai_sdk' não instalada. Execute: pip install xai_sdk", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
    
    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do XAI SDK"""
        if not self.client:
            self._initialize_client()
        
        try:
            print(f"Usando modelo XAI: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            from xai_sdk.chat import user, system
            chat = self.client.chat.create(
            model=model,
            temperature=kwargs.get('temperature', 0.7)
            )
            chat.append(system(kwargs.get("persona",DEFAULT_SYSTEM_PROMPT)))
            chat.append(user(message))
            max_tokens = kwargs.get('max_tokens', 4096)
            response = chat.sample()
            return response.content.strip()
        except Exception as e:
            print(f"Erro na chamada da API XAI SDK: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _extrair_texto_resposta_o_model(self, response):
        """Extrai texto da resposta dos modelos O"""
        try:
            segundo_item = response.output[1]
            if not segundo_item.content or len(segundo_item.content) == 0:
                return ""
            primeiro_conteudo = segundo_item.content[0]
            return getattr(primeiro_conteudo, "text", "") or ""
        except (IndexError, AttributeError):
            return ""
    
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["grok-3-fast", "grok-3-mini", "grok-3","grok4grok-4-0709"]