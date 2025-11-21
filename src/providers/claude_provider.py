import os
import sys
from typing import Any, Dict, Tuple

from anthropic import Anthropic

from .base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT


class ClaudeProvider(BaseProvider):
    """Provider para Anthropic Claude API usando a biblioteca oficial"""

    def __init__(self):
        super().__init__(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def call_api(self, message, model, max_tokens, **kwargs):
        if not self.api_key:
            raise Exception("Erro: Variável de ambiente ANTHROPIC_API_KEY não encontrada")

        if not self.client:
            raise Exception("Erro: Cliente Anthropic não inicializado")

        try:
            print(f"Usando modelo Claude: {model} (max_tokens: {max_tokens})", file=sys.stderr)
            persona = kwargs.get("persona", DEFAULT_SYSTEM_PROMPT)
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "system": persona,
                "messages": [
                    {"role": "user", "content": message}
                ]
            }

            use_stream = kwargs.get("stream", True)
            if use_stream:
                response_text, nerd_stats = self._call_with_stream(payload)
            else:
                raw_response = self.client.messages.create(**payload)
                nerd_stats = getattr(raw_response, "usage", None)
                response_text = self._extract_text(raw_response)

            if nerd_stats:
                print(f"Estatísticas para Nerds: {nerd_stats}", file=sys.stderr)

            return response_text
        except Exception as e:
            raise Exception(f"Erro na chamada da API Claude: {e}")

    def _call_with_stream(self, payload: Dict[str, Any]) -> Tuple[str, Any]:
        """Executa a chamada usando streaming (recomendado pela Anthropic)."""
        chunks = []
        final_response = None
        with self.client.messages.stream(**payload) as stream:
            for text in stream.text_stream:
                chunks.append(text)
            final_response = stream.get_final_response()
        aggregated = "".join(chunks).strip()
        if not aggregated:
            aggregated = self._extract_text(final_response)
        nerd_stats = getattr(final_response, "usage", None) if final_response else None
        return aggregated, nerd_stats

    def _extract_text(self, response) -> str:
        """Extrai o texto dos blocos retornados pela API."""
        if not response or not getattr(response, "content", None):
            return ""
        parts = []
        for block in response.content:
            text = getattr(block, "text", None)
            if text is None and isinstance(block, dict):
                text = block.get("text")
            if text:
                parts.append(text)
        return "".join(parts).strip()

    def get_available_models(self):
        """Retorna modelos disponíveis"""
        return [
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514"
        ]
