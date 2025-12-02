from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from os import path
import json
from types import SimpleNamespace

from providers.factory import ProviderFactory
from config.manager import ConfigManager
from constants import DEFAULT_SYSTEM_PROMPT
from utils.error_handler import SecureErrorHandler

app = FastAPI()
security = HTTPBearer()

class MessageRequest(BaseModel):
    texto: str = Field(..., description="Texto da mensagem")
    provider: str = Field('groq', description="Nome do provider", example="groq")
    persona: Optional[str] = Field(None, description="Persona a ser usada")
    capacidade: Optional[str] = Field('fast', description="Capacidade do modelo: fast, smart, smartest")

class MessageResponse(BaseModel):
    resposta: str
    modelo: str

def get_api_keys():
    """Carrega as chaves de API de um arquivo JSON."""
    keys_file = path.join(path.dirname(__file__), 'api.key.json')
    if not path.exists(keys_file):
        return {}
    with open(keys_file, 'r') as file:
        return json.load(file)

api_keys = get_api_keys()
VALID_OWNER = api_keys.get("nome")
VALID_KEYS = api_keys.get("chaves", [])

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida o token de autenticação."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        owner, key = token.split(":", 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Use 'owner:key'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if owner != VALID_OWNER or key not in VALID_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return owner

config_manager = ConfigManager()
provider_factory = ProviderFactory()

def _build_capacidade_args(capacidade: Optional[str]) -> SimpleNamespace:
    """Create a lightweight args object compatible with ConfigManager."""
    capa = (capacidade or 'default').lower()
    return SimpleNamespace(
        transcribe=False,
        fast=capa == 'fast',
        cheap=capa == 'cheap',
        smart=capa == 'smart',
        smartest=capa == 'smartest',
        absurdo=capa == 'absurdo',
        model=None,
        max_tokens=None
    )


@app.post("/chat", response_model=MessageResponse)
def trata_mensagem(req: MessageRequest, token: str = Depends(validate_token)):
    try:
        provider_name = (req.provider or 'groq').lower()
        persona = req.persona or DEFAULT_SYSTEM_PROMPT
        capacidade_args = _build_capacidade_args(req.capacidade)

        modelo, max_tokens, is_o_model = config_manager.get_model_config(capacidade_args, provider_name)
        print(f"Modelo: {modelo}, Max Tokens: {max_tokens}")
        
        provider = provider_factory.create_provider(provider_name)
        resposta = provider.call_api(
            req.texto, 
            modelo, 
            max_tokens, 
            is_o_model=is_o_model, 
            persona=persona
        )
        return MessageResponse(resposta=resposta, modelo=modelo)
    except Exception as e:
        SecureErrorHandler.handle_error(
            "API",
            f"Erro ao processar a mensagem: {e}"
        )
        # Retorna uma resposta de erro genérica para o cliente
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno ao processar sua solicitação."
        )

# Função para disponibilizar a API de texto
def start_text_api(host,port, log_level="debug"):
    try:
        import uvicorn
        # inicia uvicorn com Debug ativado
        uvicorn.run("API:app", host=host, port=port, reload=True, log_level=log_level)
    except Exception as e:
        SecureErrorHandler.handle_error(
            "API",
            f"Error starting Uvicorn server: {e}"
        )
