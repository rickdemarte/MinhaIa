import sys
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Classe base abstrata para providers de IA sem dependências externas"""

    def __init__(self, api_key=None):
        self.api_key = api_key

    @abstractmethod
    def call_api(self, message, model, max_tokens, **kwargs):
        """Método unificado para chamar a API do provider"""
        pass

    @abstractmethod
    def get_available_models(self):
        """Retorna os modelos disponíveis para este provider"""
        pass
