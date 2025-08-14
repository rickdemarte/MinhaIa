import os
import sys
from anthropic import Anthropic
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT


class ClaudeProvider(BaseProvider):
    """Provider para Anthropic Claude API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def call_api(self, message, model, max_tokens, **kwargs):
        if not self.api_key:
            raise Exception("Erro: Variável de ambiente ANTHROPIC_API_KEY não encontrada")

        try:
            print(f"Usando modelo Claude: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": message}
                ]
            )
            nerd_stats = getattr(response, "usage", None)
            if nerd_stats:
                print(f"Estatísticas para Nerds: {nerd_stats}")
            return response.content[0].text if response.content else ""
        except Exception as e:
            raise Exception(f"Erro na chamada da API Claude: {e}")

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return [
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514"
        ]
