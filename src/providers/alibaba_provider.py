import os
import sys
from openai import OpenAI
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT


class Qwen3Provider(BaseProvider):
    """Provider para Qwen (Alibaba) API usando a interface compatível com OpenAI"""

    def __init__(self):
        super().__init__(api_key=os.getenv('QWEN_API_KEY'))
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        ) if self.api_key else None

    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        if not self.api_key:
            print("Erro: Variável de ambiente QWEN_API_KEY não encontrada", file=sys.stderr)
            sys.exit(1)

        if is_o_model:
            print("Aviso: Modelos O não são suportados pelo Qwen", file=sys.stderr)
            return "Modelos O não são suportados pelo provider Qwen"

        try:
            print(f"Usando modelo Qwen: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": message}
                ]
            )
            nerd_stats = response.usage
            print(f"Estatísticas para Nerds: {str(nerd_stats)}")
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro na chamada da API Qwen: {e}", file=sys.stderr)
            sys.exit(1)

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"]
