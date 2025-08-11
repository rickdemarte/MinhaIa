import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT


class GrokProvider(BaseProvider):
    """Provider para XAI SDK API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('GROK_API_KEY'))
        self.client = None

    def _ensure_client(self):
        if not self.api_key:
            print("Erro: Variável de ambiente GROK_API_KEY não encontrada", file=sys.stderr)
            sys.exit(1)
        if not self.client:
            try:
                from xai_sdk import Client as XAIClient
                self.client = XAIClient(api_key=self.api_key)
            except ImportError:
                import traceback
                print("Erro: Biblioteca 'xai_sdk' não instalada. Execute: pip install xai_sdk", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                sys.exit(1)

    def call_api(self, message, model, max_tokens, **kwargs):
        self._ensure_client()
        try:
            from xai_sdk.chat import user, system
            print(f"Usando modelo Grok: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            chat = self.client.chat.create(model=model, temperature=0.7, max_output_tokens=max_tokens)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            if persona:
                chat.append(system(persona))
            chat.append(user(message))
            response = chat.sample()
            return getattr(response, "content", "")
        except Exception as e:
            print(f"Erro na chamada da API Grok: {e}", file=sys.stderr)
            sys.exit(1)

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["grok-3-fast", "grok-3-mini", "grok-3", "grok-4-0709"]
