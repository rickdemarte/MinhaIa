import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import List, Optional, Any

class GrokLangChainWrapper(BaseChatModel):
    """Wrapper LangChain para Grok XAI SDK"""
    
    def __init__(self, api_key: str, model: str = "grok-3-fast", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.model = model
        self.client = None
        
    def _initialize_client(self):
        """Inicializa o cliente XAI SDK"""
        try:
            from xai_sdk import Client as XAIClient
            self.client = XAIClient(api_key=self.api_key)
        except ImportError:
            import traceback
            print("Erro: Biblioteca 'xai_sdk' não instalada. Execute: pip install xai_sdk", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """Gera resposta usando XAI SDK"""
        if not self.client:
            self._initialize_client()
            
        try:
            from xai_sdk.chat import user, system
            chat = self.client.chat.create(
                model=self.model,
                temperature=kwargs.get('temperature', 0.7)
            )
            
            for message in messages:
                if isinstance(message, SystemMessage):
                    chat.append(system(message.content))
                elif isinstance(message, HumanMessage):
                    chat.append(user(message.content))
                    
            response = chat.sample()
            return ChatResult(generations=[ChatGeneration(message=response)])
            
        except Exception as e:
            print(f"Erro na chamada da API XAI SDK: {e}", file=sys.stderr)
            raise e
    
    @property
    def _llm_type(self) -> str:
        return "grok"

class GrokProvider(BaseProvider):
    """Provider para XAI SDK API usando LangChain"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('GROK_API_KEY'))
        self.model = None
        self.max_tokens = None
        
    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo Grok com wrapper LangChain"""
        if not self.api_key:
            print("Erro: Variável de ambiente GROK_API_KEY não encontrada", file=sys.stderr)
            sys.exit(1)
        
        return GrokLangChainWrapper(
            api_key=self.api_key,
            model=self.model or "grok-3-fast"
        )
    
    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do Grok usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens
        
        try:
            print(f"Usando modelo Grok: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            return super().call_api(message, model, max_tokens, **kwargs)
        except Exception as e:
            print(f"Erro na chamada da API Grok: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["grok-3-fast", "grok-3-mini", "grok-3","grok-4-0709"]