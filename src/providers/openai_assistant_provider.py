import os
import sys
import time
from typing import List

#from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler

class OpenAIAssistantProvider():
    """Provider para OpenAI Assistants API"""

    def __init__(self):
        super().__init__()
        self.client = None
        self.model = None
        self.max_tokens = None

    def _initialize_client(self):
        """Inicializa o cliente OpenAI"""
        try:
            from openai import OpenAI
            self.client = OpenAI()
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
            is_o_model = kwargs.get("is_o_model", False)

            print(f"Usando Assistants API OpenAI: {model} (max_tokens: {max_tokens})", file=sys.stderr)

            print("Criando assistente...")

            tools = [{"type": "file_search"}]
            if not is_o_model:
                tools.append({"type": "code_interpreter"})

            assistant = self.client.beta.assistants.create(
                model=model,
                instructions=persona,
                tools=tools,
            )

            print("Criando thread...")
            thread = self.client.beta.threads.create()

            # Processamento correto dos arquivos
            attachments = []
            for file_path in files:
                print(f"Processando arquivo {file_path}...")
                try:
                    with open(file_path, "rb") as f:
                        uploaded = self.client.files.create(file=f, purpose="assistants")
                        # Estrutura correta para attachments
                        # Se for o3-mini, não carrega code_interpreter
                        attachments.append({
                            "file_id": uploaded.id,
                            "tools": tools
                        })
                        
                except Exception as e:
                    print(f"Erro ao enviar arquivo {file_path}: {e}", file=sys.stderr)
            
            # Correção na criação da mensagem
            message_data = {
                "thread_id": thread.id,
                "role": "user",
                "content": message,
            }
            
            # Adiciona attachments apenas se houver arquivos
            if attachments:
                message_data["attachments"] = attachments

            self.client.beta.threads.messages.create(**message_data)

            print("Criando fila de processamento...")
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )

            # Aguarda conclusão do processamento
            while True:
                print(f"Verificando status do assistente {assistant.id}")
                if run.status == "completed":
                    break
                if run.status in {"failed", "expired", "cancelled"}:
                    raise Exception(f"Run finalizado com status {run.status}\nAssistente: {assistant.id}\nThread: {thread.id}")
                print(f"Status da fila: {run.status}")
                time.sleep(1)

            # Recupera a resposta
            messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="desc")
            for msg in messages.data:
                if msg.role == "assistant" and msg.content:
                    conteudo = msg.content[0].text.value
                    if conteudo:
                        # Limpeza opcional - remove recursos após uso
                        try:
                            self.client.beta.assistants.delete(assistant.id)
                            # Note: threads são automaticamente limpas, mas você pode deletar se necessário
                        except:
                            pass  # Ignora erros de limpeza
                        
                        return conteudo
            
            return ""
            
        except Exception as e:
            print(f"Erro ao chamar Assistants API OpenAI: {e}", file=sys.stderr)
            # Tenta limpar recursos em caso de erro
            try:
                if 'assistant' in locals():
                    self.client.beta.assistants.delete(assistant.id)
            except:
                pass
            sys.exit(1)

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return ["gpt-4o-mini", "gpt-4.1-nano", "gpt-4.1", "o3-mini"]