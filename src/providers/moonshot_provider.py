import os
import sys
from openai import OpenAI
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class MoonshotProvider(BaseProvider):
    """Provider para Moonshot/Kimi usando API compatível com OpenAI."""

    def __init__(self):
        super().__init__(api_key=os.getenv('KIMI_API_KEY'))
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.moonshot.ai/v1") if self.api_key else None

    def call_api(self, message, model, max_tokens, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("KIMI_APY_KEY and KIMI_API_KEY not found"),
                context={"provider": "moonshot"}
            )
            raise Exception("KIMI_APY_KEY and KIMI_API_KEY not found")

        try:
            persona = kwargs.get("persona") or DEFAULT_SYSTEM_PROMPT
            print(f"Usando modelo Kimi: {model} - (max_tokens: {max_tokens}) {persona}", file=sys.stderr)
            print(f"Persona: {persona}")
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": message}
                ]
            )
            nerd_stats = response.usage
            print(f"Estatisticas para Nerds: {str(nerd_stats)}")
            return response.choices[0].message.content or ""
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "moonshot", "model": model}
            )
            raise e

    def get_available_models(self):
        """Retorna modelos conhecidos do provider Moonshot/Kimi."""
        return [
            "kimi-k2-turbo-preview",
            "kimi-k2-0711-preview",
            "kimi-k2-0905-preview",
            "kimi-k2-thinking",
            "kimi-k2.5",
        ]
