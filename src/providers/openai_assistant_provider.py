import os
import sys
from pathlib import Path
from typing import List, Tuple

from openai import OpenAI

from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler


class OpenAIAssistantProvider(BaseProvider):
    """Provider OpenAI baseado em Responses API com suporte a ferramentas."""

    def __init__(self):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def _upload_files(self, files: List[str]) -> Tuple[List[str], List[dict]]:
        uploaded_file_ids = []
        input_files = []

        for file_path in files:
            print(f"Processando arquivo {file_path}...", file=sys.stderr)
            with open(file_path, "rb") as file_handle:
                uploaded = self.client.files.create(file=file_handle, purpose="user_data")
                uploaded_file_ids.append(uploaded.id)
                input_files.append(
                    {
                        "type": "input_file",
                        "file_id": uploaded.id,
                        "filename": Path(file_path).name,
                    }
                )

        return uploaded_file_ids, input_files

    def _cleanup_files(self, file_ids: List[str]) -> None:
        for file_id in file_ids:
            try:
                self.client.files.delete(file_id)
            except Exception:
                pass

    def call_api(self, message: str, model: str, max_tokens: int, **kwargs):
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("OPENAI_API_KEY not found"),
                context={"provider": "assistant"},
            )
            raise Exception("OPENAI_API_KEY not found")

        persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
        is_o_model = kwargs.get("is_o_model", False)
        temperature = kwargs.get("temperature", 0.7)
        files: List[str] = kwargs.get("files") or []
        uploaded_file_ids: List[str] = []

        try:
            print(
                f"Usando OpenAI Responses com ferramentas: {model} (max_tokens: {max_tokens})",
                file=sys.stderr,
            )

            input_content = [{"type": "input_text", "text": message}]
            if files:
                uploaded_file_ids, input_files = self._upload_files(files)
                input_content.extend(input_files)

            params = {
                "model": model,
                "instructions": persona if not is_o_model else O_MODEL_SYSTEM_PROMPT,
                "max_output_tokens": max_tokens,
                "input": [
                    {
                        "role": "user",
                        "content": input_content,
                    }
                ],
            }

            tools = []
            if not is_o_model:
                code_interpreter = {
                    "type": "code_interpreter",
                    "container": {"type": "auto"},
                }
                if uploaded_file_ids:
                    code_interpreter["container"]["file_ids"] = uploaded_file_ids
                tools.append(code_interpreter)
                params["temperature"] = temperature

            if tools:
                params["tools"] = tools
                params["include"] = ["code_interpreter_call.outputs"]

            response = self.client.responses.create(**params)
            nerd_stats = response.usage
            print(f"Estatísticas para Nerds: {str(nerd_stats)}", file=sys.stderr)

            if getattr(response, "output_text", None):
                return response.output_text

            for item in getattr(response, "output", []):
                if item.type == "message" and item.content:
                    for content in item.content:
                        text = getattr(content, "text", None)
                        if text:
                            return text

            return ""
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "assistant", "model": model},
            )
            raise e
        finally:
            if uploaded_file_ids and self.client:
                self._cleanup_files(uploaded_file_ids)

    def get_available_models(self):
        """Retorna modelos disponíveis."""
        return ["gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.4-pro", "gpt-4.1"]
