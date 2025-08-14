import os
import sys
from pathlib import Path
from openai import OpenAI
from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class OpenAIProvider(BaseProvider):
    """Provider para OpenAI API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        # Alias para suportar chamadas no formato `client.response.delete(id)`
        # mantendo compatibilidade com o SDK oficial (`client.responses.delete`).
        if self.client and not hasattr(self.client, "response"):
            class _ResponseDeleteProxy:
                def __init__(self, openai_client):
                    self._openai_client = openai_client

                def delete(self, response_id):
                    # Encaminha para a API oficial `responses.delete`.
                    return self._openai_client.responses.delete(response_id)

            self.client.response = _ResponseDeleteProxy(self.client)
        self.history_file = Path.home() / '.minhaia/response.id'

    def _load_history(self):
        if self.history_file.exists():
            return self.history_file.read_text().strip()
        return None

    def _save_history(self, response_id):
        try:
            self.history_file.write_text(response_id)
        except Exception:
            pass

    def _delete_history(self):
        if self.history_file.exists():
            try:
                response_id = self.history_file.read_text().strip()
                if self.client:
                    try:
                        # Usa o alias solicitado: `client.response.delete(id)`
                        self.client.response.delete(response_id)
                    except Exception:
                        pass
            finally:
                try:
                    self.history_file.unlink()
                except Exception:
                    pass

    def call_api(self, message, model, max_tokens, is_o_model=False, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("OPENAI_API_KEY not found"),
                context={"provider": "openai"}
            )

        try:
            persona = kwargs.get("persona", O_MODEL_SYSTEM_PROMPT if is_o_model else DEFAULT_SYSTEM_PROMPT)
            persistent = kwargs.get("persistent")
            print(f"Usando modelo OpenAI: {model} - (max_tokens: {max_tokens}) {persona}", file=sys.stderr)

            prev_id = None
            if persistent == 'no':
                print("Limpando conversa anterior")
                self._delete_history()
            else:
                prev_id = self._load_history()
                print(f"Continuando conversa id: {prev_id}", file=sys.stderr)

            params = {
                "model": model,
                "max_output_tokens": max_tokens,
                "input": [
                    {"role": "system", "content": persona},
                    {"role": "user", "content": message}
                ]
            }

            if persistent != 'no':
                params["store"] = True
                if prev_id:
                    params["previous_response_id"] = prev_id

            response = self.client.responses.create(**params)

            if persistent == 'yes':
                self._save_history(response.id)

            nerd_stats = response.usage
            print(f"Estatísticas para Nerds: {str(nerd_stats)}")
            return self._extrair_texto_resposta(response)
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "openai", "model": model}
            )

    def _extrair_texto_resposta(self, response):
        try:
            for item in response.output:
                if item.content and len(item.content) > 0:
                    primeiro = item.content[0]
                    texto = getattr(primeiro, "text", None)
                    if texto:
                        return texto
            return ""
        except Exception:
            return ""

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["gpt-4o-mini", "gpt-4o", "chatgpt-4o-latest", "o3-mini", "o3"]
