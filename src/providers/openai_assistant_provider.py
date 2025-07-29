import os
import sys
import time
from typing import List

from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler

class OpenAIAssistantProvider(BaseProvider):
    """Provider para OpenAI Assistants API"""

    def __init__(self):
        super().__init__(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = None
        self.model = None
        self.max_tokens = None

    def _initialize_client(self):
        """Inicializa o cliente OpenAI"""
        if not self.api_key:
            SecureErrorHandler.handle_error(
                "api_key_missing",
                Exception("OPENAI_API_KEY not found"),
                context={"provider": "openai_assistant"},
            )

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            print("Erro: Biblioteca 'openai' não instalada. Execute: pip install openai", file=sys.stderr)
            sys.exit(1)

    def call_api(self, message: str, model: str, max_tokens: int, **kwargs):
        """Chama a Assistants API"""
        if not self.client:
            self._initialize_client()

        self.model = model
        self.max_tokens = max_tokens

        try:
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            files: List[str] = kwargs.get("files") or []
            print(f"Usando Assistants API OpenAI: {model} (max_tokens: {max_tokens})", file=sys.stderr)

            assistant = self.client.beta.assistants.create(
                model=model,
                instructions=persona,
                tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
            )

            thread = self.client.beta.threads.create()

            file_ids = []
            for file_path in files:
                try:
                    with open(file_path, "rb") as f:
                        uploaded = self.client.files.create(file=f, purpose="assistants")
                        file_ids.append(uploaded.id)
                except Exception as e:
                    print(f"Erro ao enviar arquivo {file_path}: {e}", file=sys.stderr)

            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message,
                file_ids=file_ids if file_ids else None,
            )

            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )

            while True:
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run.status == "completed":
                    break
                if run.status in {"failed", "expired", "cancelled"}:
                    raise Exception(f"Run finalizado com status {run.status}")
                time.sleep(1)

            messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="desc")
            for msg in messages.data:
                if msg.role == "assistant" and msg.content:
                    conteudo = msg.content[0].text.value
                    if conteudo:
                        return conteudo
            return ""
        except Exception as e:
            SecureErrorHandler.handle_error(
                "api_error",
                e,
                context={"provider": "openai_assistant", "model": model},
            )

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["gpt-4o-mini", "gpt-4o", "chatgpt-4o-latest", "o3-mini", "o3"]
