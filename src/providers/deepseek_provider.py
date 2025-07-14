import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT

import requests

class DeepSeekProvider(BaseProvider):
    """Provider para DeepSeek AI API"""

    def __init__(self):
        super().__init__(api_key=os.getenv('DEEPSEEK_API_KEY'))
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do DeepSeek"""
        if not self.api_key:
            print("Erro: Variável de ambiente DEEPSEEK_API_KEY não encontrada", file=sys.stderr)
            print("Execute: export DEEPSEEK_API_KEY='sua_chave_aqui'", file=sys.stderr)
            sys.exit(1)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": kwargs.get("persona",DEFAULT_SYSTEM_PROMPT)},
                {"role": "user", "content": message}
            ],
            "max_tokens": max_tokens,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0)
        }

        try:
            print(f"Usando modelo DeepSeek: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"Erro na resposta da API DeepSeek: {response.status_code} - {response.text}", file=sys.stderr)
                sys.exit(1)
            
            data = response.json()
            return data['choices'][0]['message']['content']
        
        except Exception as e:
            print(f"Erro na chamada da API DeepSeek: {e}", file=sys.stderr)
            sys.exit(1)

    def get_available_models(self):
        """Retorna modelos disponíveis da DeepSeek"""
        return [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-coder-33b",
            "deepseek-llm",
        ]
