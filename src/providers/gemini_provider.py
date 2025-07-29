import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler
from langchain_core.language_models.chat_models import BaseChatModel


class GeminiProvider(BaseProvider):
    """Provider para Google Gemini API usando LangChain"""

    def __init__(self):
        super().__init__(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = None
        self.max_tokens = None

    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo Gemini usando LangChain"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("GOOGLE_API_KEY not found"),
                context={"provider": "gemini"}
            )

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                google_api_key=self.api_key,
                model=self.model or "models/gemini-1.5-pro-latest",
                max_output_tokens=self.max_tokens or 2000,
                temperature=0.7
            )
        except ImportError as e:
            SecureErrorHandler.handle_error(
                "dependency_missing",
                e,
                context={"provider": "gemini", "library": "langchain-google-genai"}
            )

    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do Gemini usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens

        try:
            print(f"Usando modelo Gemini: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            return super().call_api(message, model, max_tokens, **kwargs)
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
            "models/gemini-pro"
        ]

