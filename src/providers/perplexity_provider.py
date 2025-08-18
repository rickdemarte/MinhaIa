import os
from perplexipy import PerplexityClient
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler

class PerplexityProvider(BaseProvider):
    def __init__(self):
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            self.handle_missing_api_key()
        self.client = PerplexityClient(key=api_key)

    def handle_missing_api_key(self):
        SecureErrorHandler.handle_error(
            "api_key_missing",
            Exception("PERPLEXITY_API_KEY não encontrada no ambiente."),
            context={"provider": "perplexity"}
        )

    def call_api(self, message, model, max_tokens, **kwargs):
        try:
            response = self.client.query(
                str(self.prepare_messages(message, kwargs))
            )
            return response
        except Exception as e:
            return self.handle_api_error(e, model)

    def prepare_messages(self, message, kwargs):
        persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
        return [
            {"role": "system", "content": persona},
            {"role": "user", "content": message},
        ]

    def handle_api_error(self, error, model):
        SecureErrorHandler.handle_error(
            "api_error",
            error,
            context={"provider": "perplexity", "model": model}
        )
        return None

    def handle_list_models_error(self, error):
        SecureErrorHandler.handle_error(
            "api_error",
            error,
            context={"provider": "perplexity", "operation": "list_models"}
        )
        return []

    def get_available_models(self):
        models = self.client.models # lists all models supported by Perplexity AI
        return models