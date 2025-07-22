from pydantic import BaseModel, Field
from fastapi import FastAPI, Header, HTTPException
from typing import Optional

from providers.factory import ProviderFactory
from config.manager import ConfigManager

from constants import DEFAULT_SYSTEM_PROMPT

from utils.argumentos import CLIArgumentParser
from utils.error_handler import SecureErrorHandler

app = FastAPI()

class MessageRequest(BaseModel):
    texto: str = Field(..., description="Texto da mensagem")
    provider: str = Field('groq', description="Nome do provider", example="groq")
    persona: Optional[str] = Field(None, description="Persona a ser usada")
    capacidade: Optional[str] = Field('fast', description="Capacidade do modelo: fast, smart, smartest")

class MessageResponse(BaseModel):
    resposta: str
    modelo: str

config_manager = ConfigManager()
provider_factory = ProviderFactory()

@app.post("/chat", response_model=MessageResponse)

def trata_mensagem(req: MessageRequest, chave: str = Header(None)):
    argumentos = CLIArgumentParser().parse_args()
    if argumentos.secure:
        # Carrega as chaves do arquivo api.env para a variável chaves
        from dotenv import load_dotenv
        from os import path, getenv
        import ast
        load_dotenv(path.join(path.dirname(__file__), 'api.env'))
        raw_keys = getenv('RIBEIRO_API_KEYS', '')
        # Remove espaços e aspas extras, suporta formato JSON ou CSV
        if raw_keys.strip().startswith('['):
            chaves = ast.literal_eval(raw_keys)
        else:
            chaves = [k.strip().strip('"').strip("'") for k in raw_keys.split(',') if k.strip()]
        if not chave or chave not in chaves:
            raise HTTPException(status_code=401, detail=f"API key inválida ou ausente.")
    try:
        argumentos.provider = req.provider or 'groq'
        capacidade = req.capacidade or 'default'
        if capacidade == 'absurdo' and argumentos.provider == 'openai':
            is_o_model = True
        else:
            is_o_model = False
        persona = req.persona
        texto = req.texto
        argumentos.persona = persona or DEFAULT_SYSTEM_PROMPT
    except Exception as e:
        SecureErrorHandler.handle_error(
            "API",
            e
        )
        return MessageResponse(resposta=f"Erro ao processar a mensagem. Verifique os parâmetros fornecidos: {e}")
    
    # Seleciona modelo baseado na capacidade
    modelo, max_tokens, is_o_model = config_manager.get_model_config(argumentos, argumentos.provider)
    print(f"Modelo: {modelo}, Max Tokens: {max_tokens}")
    # Chama o provider
    provider = provider_factory.create_provider(argumentos.provider)
    resposta = provider.call_api(texto, modelo, max_tokens, is_o_model=is_o_model, persona=argumentos.persona)
    return MessageResponse(resposta=resposta, modelo=modelo)

# Função para disponibilizar a API de texto
def start_text_api(host,port):
    try:
        import uvicorn
        uvicorn.run("API:app", host=host, port=port, reload=True)
    except Exception as e:
        SecureErrorHandler.handle_error(
            "API",
            f"Error starting Uvicorn server: {e}"
        )
