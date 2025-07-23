import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

class Qwen3Provider(BaseProvider):
    """Provider para Qwen (Alibaba) API usando LangChain"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('QWEN_API_KEY'))
        self.model = None
        self.max_tokens = None
        
    def _initialize_llm(self) -> BaseChatModel:
        """Inicializa o modelo Qwen usando LangChain OpenAI wrapper"""
        if not self.api_key:
            print("Erro: Variável de ambiente QWEN_API_KEY não encontrada", file=sys.stderr)
            sys.exit(1)
        
        try:
            return ChatOpenAI(
                api_key=self.api_key,
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                model=self.model or "qwen-turbo",
                max_tokens=self.max_tokens or 2000,
                temperature=0.7
            )
        except ImportError:
            print("Erro: Biblioteca 'langchain-openai' não instalada. Execute: pip install langchain-openai", file=sys.stderr)
            sys.exit(1)
    
    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        """Chama a API do Qwen usando LangChain"""
        self.model = model
        self.max_tokens = max_tokens
        
        try:
            print(f"Usando modelo Qwen: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            
            if is_o_model:
                print("Aviso: Modelos O não são suportados pelo Qwen", file=sys.stderr)
                return "Modelos O não são suportados pelo provider Qwen"
            else:
                return super().call_api(message, model, max_tokens, **kwargs)
                
        except Exception as e:
            print(f"Erro na chamada da API Qwen: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"]