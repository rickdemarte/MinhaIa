import os
import sys
from openai import OpenAI
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class DeepSeekProvider(BaseProvider):
    """Provider para DeepSeek AI API usando a interface compatível com OpenAI"""

    def __init__(self):
        super().__init__(api_key=os.getenv('DEEPSEEK_API_KEY'))
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com") if self.api_key else None

    def call_api(self, message, model, max_tokens, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("DEEPSEEK_API_KEY not found"),
                context={"provider": "deepseek"}
            )

        try:
            print(f"Usando modelo DeepSeek: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
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
            print(f"Estatísticas para Nerds: {str(nerd_stats)}")
            return response.choices[0].message.content
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "deepseek", "model": model}
            )

    def get_available_models(self):
        """Retorna modelos disponíveis da DeepSeek"""
        return [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-coder-33b",
            "deepseek-llm",
        ]
