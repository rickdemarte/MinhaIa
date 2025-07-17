import os
import sys
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler

import requests

class DeepSeekProvider(BaseProvider):
    """Provider para DeepSeek AI API"""

    def __init__(self):
        super().__init__(api_key=os.getenv('DEEPSEEK_API_KEY'))
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def call_api(self, message, model, max_tokens, **kwargs):
        """Chama a API do DeepSeek"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("DEEPSEEK_API_KEY not found"),
                context={"provider": "deepseek"}
            )

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
                error_msg = f"API returned status {response.status_code}"
                if response.status_code == 429:
                    SecureErrorHandler.handle_error(
                        "rate_limit",
                        Exception(error_msg),
                        context={"provider": "deepseek", "status_code": response.status_code}
                    )
                else:
                    SecureErrorHandler.handle_error(
                        "api_error",
                        Exception(error_msg),
                        context={"provider": "deepseek", "status_code": response.status_code}
                    )
            
            data = response.json()
            return data['choices'][0]['message']['content']
        
        except requests.exceptions.ConnectionError as e:
            SecureErrorHandler.handle_error(
                "network_error",
                e,
                context={"provider": "deepseek"}
            )
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "deepseek", "model": model}
            )

    def get_available_models(self):
        """Retorna modelos disponíveis da DeepSeek"""
        return [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-coder-33b",
            "deepseek-llm",
        ]
