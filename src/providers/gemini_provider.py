import os
import sys
import google.generativeai as genai
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class GeminiProvider(BaseProvider):
    """Provider para Google Gemini API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('GOOGLE_API_KEY'))
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model = None

    def call_api(self, message, model, max_tokens, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("GOOGLE_API_KEY not found"),
                context={"provider": "gemini"}
            )

        try:
            print(f"Usando modelo Gemini: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            generative_model = genai.GenerativeModel(model)
            prompt = f"{persona}\n\n{message}"
            response = generative_model.generate_content(
                [prompt],
                generation_config={"max_output_tokens": max_tokens, "temperature": 0.7}
            )
            return response.text or ""
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "gemini", "model": model}
            )

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return [
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-flash-latest",
            "models/gemini-pro",
        ]
