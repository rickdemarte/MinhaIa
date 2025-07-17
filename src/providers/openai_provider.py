import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler

class OpenAIProvider(BaseProvider):
    """Provider para OpenAI API"""
    
    def __init__(self):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = None
        
    def _initialize_client(self):
        """Inicializa o cliente OpenAI"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("OPENAI_API_KEY not found"),
                context={"provider": "openai"}
            )
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError as e:
            SecureErrorHandler.handle_error(
                "dependency_missing",
                e,
                context={"provider": "openai", "library": "openai"}
            )
    
    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        """Chama a API da OpenAI"""
        if not self.client:
            self._initialize_client()
        
        try:
            personalidade = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            print(f"Usando modelo OpenAI: {model} - (max_tokens: {max_tokens}) {personalidade}", file=sys.stderr)
            
            if is_o_model:
                print("Aviso: Modelos O podem levar mais tempo para processar respostas complexas", file=sys.stderr)
                response = self.client.responses.create(
                    model=model,
                    reasoning={"effort": "medium"},
                    input=[
                        {"role": "system", "content": kwargs.get("persona",O_MODEL_SYSTEM_PROMPT)},
                        {"role": "user", "content": message}
                    ]
                )
                return self._extrair_texto_resposta_o_model(response)
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": kwargs.get("persona",DEFAULT_SYSTEM_PROMPT)},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "openai", "model": model}
            )
    
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