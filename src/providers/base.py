import sys
from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

class BaseProvider(ABC):
    """Classe base abstrata para providers de IA usando LangChain"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.llm = None
    
    @abstractmethod
    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo LangChain específico do provider"""
        pass
    
    def call_api(self, message, model, max_tokens, **kwargs):
        """Método unificado para chamar a API usando LangChain"""
        if not self.llm:
            self.llm = self._initialize_llm()
        
        # Preparar mensagens
        messages = []
        
        # Adicionar mensagem do sistema se fornecida
        if 'persona' in kwargs and kwargs['persona']:
            messages.append(SystemMessage(content=kwargs['persona']))
        
        # Adicionar mensagem do usuário
        messages.append(HumanMessage(content=message))
        
        # Chamar o modelo
        response = self.llm.invoke(messages)
        nerd_stats = response.response_metadata.get("token_usage")
        print(f"Estatísticas para Nerds: {str(nerd_stats)}")
        return response.content
    
    @abstractmethod
    def get_available_models(self):
        """Retorna os modelos disponíveis para este provider"""
        pass