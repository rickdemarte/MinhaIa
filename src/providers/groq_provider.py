import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

class GroqProvider(BaseProvider):
    """Provider para Groq API usando LangChain"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('GROQ_API_KEY'))
        self.model = None
        self.max_tokens = None
        self.is_o_model = False
        
    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo Groq LangChain"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("GROQ_API_KEY not found"),
                context={"provider": "groq"}
            )
        
        try:
            return ChatGroq(
                api_key=self.api_key,
                model=self.model or "llama-3.3-70b-versatile",
                max_tokens=self.max_tokens or 2000,
                temperature=0.7
            )
        except ImportError as e:
            SecureErrorHandler.handle_error(
                "dependency_missing",
                e,
                context={"provider": "groq", "library": "langchain-groq"}
            )
    
    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        """Chama a API da Groq usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens
        self.is_o_model = is_o_model
        
        try:
            personalidade = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            print(f"Usando modelo Groq: {model} - (max_tokens: {max_tokens}) {personalidade}", file=sys.stderr)
            
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
                context={"provider": "groq", "model": model}
            )
    
    def _handle_o_model_direct(self, message, model, kwargs):
        """Mantém o tratamento direto para modelos O até LangChain suportar"""
        from groq import Groq
        client = Groq(api_key=self.api_key)
        
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
        nerd_stats = response.response_metadata.get("token_usage")
        print(f"\nEstatísticas para Nerds: {str(nerd_stats)}")
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
        return [
            "deepseek-r1-distill-llama-70b", 
            "meta-llama/llama-4-maverick-17b-128e-instruct", 
            "llama-3.3-70b-versatile", 
            "llama-3.1-8b-instant", 
            "mistral-saba-24b",
            "qwen/qwen3-32b"]