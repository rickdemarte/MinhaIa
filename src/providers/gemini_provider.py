import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class GeminiProvider(BaseProvider):
    """Provider para Google Gemini API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('GOOGLE_API_KEY'))
        self.client = None
        self.types = None
        if self.api_key:
            self._initialize_client()

    def _initialize_client(self):
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            SecureErrorHandler.handle_error(
                "dependency_missing",
                exc,
                context={"provider": "gemini", "library": "google.genai"},
            )
            raise exc

        self.client = genai.Client(api_key=self.api_key)
        self.types = types

    def call_api(self, message, model, max_tokens, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("GOOGLE_API_KEY not found"),
                context={"provider": "gemini"}
            )
            raise Exception("GOOGLE_API_KEY not found")

        if self.client is None or self.types is None:
            self._initialize_client()

        try:
            print(f"Usando modelo Gemini: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            temperature = kwargs.get("temperature", 0.7)
            response = self.client.models.generate_content(
                model=model,
                contents=message,
                config=self.types.GenerateContentConfig(
                    system_instruction=persona,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text or ""
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "gemini", "model": model}
            )
            raise e

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return [
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ]
