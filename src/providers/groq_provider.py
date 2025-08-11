import os
import sys
from groq import Groq
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class GroqProvider(BaseProvider):
    """Provider para Groq API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('GROQ_API_KEY'))
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("GROQ_API_KEY not found"),
                context={"provider": "groq"}
            )

        try:
            persona = kwargs.get("persona", O_MODEL_SYSTEM_PROMPT if is_o_model else DEFAULT_SYSTEM_PROMPT)
            print(f"Usando modelo Groq: {model} - (max_tokens: {max_tokens}) {persona}", file=sys.stderr)

            if is_o_model:
                response = self.client.responses.create(
                    model=model,
                    reasoning={"effort": "medium"},
                    max_output_tokens=max_tokens,
                    input=[
                        {"role": "system", "content": persona},
                        {"role": "user", "content": message}
                    ]
                )
                return self._extrair_resposta_o_model(response)
            else:
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
                print(f"\nEstatísticas para Nerds: {str(nerd_stats)}")
                return response.choices[0].message.content
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "groq", "model": model}
            )

    def _extrair_resposta_o_model(self, response):
        nerd_stats = response.response_metadata.get("token_usage")
        print(f"\nEstatísticas para Nerds: {str(nerd_stats)}")
        try:
            for item in response.output:
                if item.content and len(item.content) > 0:
                    texto = getattr(item.content[0], "text", None)
                    if texto:
                        return texto
            return ""
        except Exception:
            return ""

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return [
            "deepseek-r1-distill-llama-70b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mistral-saba-24b",
            "qwen/qwen3-32b"
        ]
