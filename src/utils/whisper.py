from posix import environ
import sys
import openai
from pathlib import Path
from providers.base import BaseProvider
from constants import DEFAULT_SYSTEM_PROMPT, O_MODEL_SYSTEM_PROMPT

class WhisperProvider(BaseProvider):
    """Provider para OpenAI Whisper API"""

    def __init__(self):
        super().__init__(api_key=environ.get('OPENAI_API_KEY'))
        self.client = None

    def _initialize_client(self):
        """Inicializa o cliente OpenAI"""
        if not self.api_key:
            print("Erro: Variável de ambiente OPENAI_API_KEY não encontrada", file=sys.stderr)
            return

        try:
            openai.api_key = self.api_key
        except ImportError:
            print("Erro: Biblioteca 'openai' não instalada. Execute: pip install openai", file=sys.stderr)

    def call_api(self, audio_file_path, modelo, max_tokens, **kwargs):
        """Chama a API da OpenAI"""
        if not self.client:
            self._initialize_client()
        if not Path(audio_file_path).is_file():
            print(f"Erro: Arquivo de áudio '{audio_file_path}' não encontrado", file=sys.stderr)
            return None

        audio_file = open(audio_file_path, "rb")

        response = openai.Audio.transcribe(
            model=modelo,
            file=audio_file,
            response_format="text"
        )

        audio_file.close()
    
        return response
    
    def get_available_models(self):
        """Retorna a lista de modelos disponíveis para o Whisper"""
        # Aqui você pode retornar uma lista com os modelos disponíveis.
        return ["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"]  # Exemplo de modelos
    