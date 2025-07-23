import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

class OpenAIProvider(BaseProvider):
    """Provider para OpenAI API usando LangChain"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = None
        self.max_tokens = None
        self.is_o_model = False
        
    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo OpenAI LangChain"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("OPENAI_API_KEY not found"),
                context={"provider": "openai"}
            )
        
        try:
            return ChatOpenAI(
                api_key=self.api_key,
                model=self.model or "gpt-4o-mini",
                max_tokens=self.max_tokens or 2000,
                temperature=0.7
            )
        except ImportError as e:
            SecureErrorHandler.handle_error(
                "dependency_missing",
                e,
                context={"provider": "openai", "library": "langchain-openai"}
            )
    
    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        """Chama a API da OpenAI usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens
        self.is_o_model = is_o_model
        
        try:
            personalidade = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            print(f"Usando modelo OpenAI: {model} - (max_tokens: {max_tokens}) {personalidade}", file=sys.stderr)
            
            if is_o_model:
                print("Aviso: Modelos O podem levar mais tempo para processar respostas complexas", file=sys.stderr)
                # Para modelos O, ainda usamos a API direta pois LangChain pode não suportar
                return self._handle_o_model_direct(message, model, kwargs)
            else:
                # Usar LangChain para modelos regulares
                return super().call_api(message, model, max_tokens, **kwargs)
                
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "openai", "model": model}
            )
    
    def _handle_o_model_direct(self, message, model, kwargs):
        """Mantém o tratamento direto para modelos O até LangChain suportar"""
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        response = client.responses.create(
            model=model,
            reasoning={"effort": "medium"},
            input=[
                {"role": "system", "content": kwargs.get("persona", O_MODEL_SYSTEM_PROMPT)},
                {"role": "user", "content": message}
            ]
        )
        return self._extrair_texto_resposta_o_model(response)
    
    def _extrair_texto_resposta_o_model(self, response):
        """Extrai texto da resposta dos modelos O"""
        try:
            segundo_item = response.output[1]
            if not segundo_item.content or len(segundo_item.content) == 0:
                return ""
            primeiro_conteudo = segundo_item.content[0]
            return getattr(primeiro_conteudo, "text", "") or ""
        except (IndexError, AttributeError):
            return ""
    
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["gpt-4o-mini", "gpt-4o", "chatgpt-4o-latest", "o3-mini", "o3"]