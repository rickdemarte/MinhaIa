from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Classe base abstrata para providers de IA"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    @abstractmethod
    def call_api(self, message, model, max_tokens, **kwargs):
        """Método abstrato para chamar a API"""
        pass
    
    @abstractmethod
    def get_available_models(self):
        """Retorna os modelos disponíveis para este provider"""
        pass