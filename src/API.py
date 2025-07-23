from pydantic import BaseModel, Field
from fastapi import FastAPI, Header, HTTPException
from typing import Optional
from os import path, getenv
import json

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

class BancoDeDados:
    # Carrega chaves de um arquivo JSON
    def __init__(self):
        banco = path.join(path.dirname(__file__), 'api.key.json')
        if not path.exists(banco):
            raise FileNotFoundError(f"Arquivo de banco de dados {banco} não encontrado.")
        with open(banco, 'r') as file:
            chaves = json.load(file)
        self.__chaves = chaves.get('chaves', [])
        self.__owner = chaves.get('nome', '')
    
    def get_chaves(self):
        return self.__chaves, self.__owner

config_manager = ConfigManager()
provider_factory = ProviderFactory()

def require_auth(header: str):
    chaves, owners = BancoDeDados().get_chaves()
    owner = header.split(':')[0] if header else "None"
    chave = header.split(':')[1] if header else "None"
    if owner == owners:
        if chave in chaves:
            return True
    raise HTTPException(status_code=401, detail=f"Token de autenticação inválido ou expirado \n Fornecido ({chave})")
    


@app.post("/chat", response_model=MessageResponse)
def trata_mensagem(req: MessageRequest, header: str = Header(None)):
    argumentos = CLIArgumentParser().parse_args()
    try:
        if argumentos.secure:
            ## mostra no console a chave recebida
            print(f"Chave recebida: {header}")
            if not require_auth(header):
                raise HTTPException(status_code=401, detail="Token não validado")
            
        argumentos.provider = req.provider or 'groq'
        capacidade = req.capacidade or 'default'
        if capacidade == 'absurdo' and argumentos.provider == 'openai':
            is_o_model = True
        else:
            is_o_model = False
        persona = req.persona
        texto = req.texto
        argumentos.persona = persona or DEFAULT_SYSTEM_PROMPT
        
        # Seleciona modelo baseado na capacidade
        modelo, max_tokens, is_o_model = config_manager.get_model_config(argumentos, argumentos.provider)
        print(f"Modelo: {modelo}, Max Tokens: {max_tokens}")
        # Chama o provider
        provider = provider_factory.create_provider(argumentos.provider)
        resposta = provider.call_api(texto, modelo, max_tokens, is_o_model=is_o_model, persona=argumentos.persona)
        return MessageResponse(resposta=resposta, modelo=modelo)
    except Exception as e:
        SecureErrorHandler.handle_error(
            "API",
            f"Erro ao processar a mensagem: {e}"
        )
        return MessageResponse(resposta=f"Erro ao processar a mensagem: {e}")

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
