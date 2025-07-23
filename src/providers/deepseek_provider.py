import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

class DeepSeekProvider(BaseProvider):
    """Provider para DeepSeek AI API usando LangChain com OpenAI-compatible API"""

    def __init__(self):
        super().__init__(api_key=os.getenv('DEEPSEEK_API_KEY'))
        self.model = None
        self.max_tokens = None

    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo DeepSeek usando LangChain OpenAI wrapper"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("DEEPSEEK_API_KEY not found"),
                context={"provider": "deepseek"}
            )

        try:
            return ChatOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
                model=self.model or "deepseek-chat",
                max_tokens=self.max_tokens or 2000,
                temperature=0.7
            )
        except ImportError as e:
            SecureErrorHandler.handle_error(
                "dependency_missing",
                e,
                context={"provider": "deepseek", "library": "langchain-openai"}
            )

    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do DeepSeek usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens
        
        try:
            print(f"Usando modelo DeepSeek: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            return super().call_api(message, model, max_tokens, **kwargs)
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
