## Documentação da API

Também vou criar um arquivo `requirements.txt` atualizado:

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
openai
anthropic
requests
PyPDF2
boto3
```

E um exemplo de cliente para consumir a API:

```python
# client_example.py
"""
Exemplo de cliente para consumir a API
"""

import requests
import base64
import json

API_URL = "http://localhost:8000"

def example_simple_chat():
    """Exemplo de chat simples"""
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "Olá, como você está?",
            "provider": "openai",
            "model_type": "fast",
            "output_format": "plain"
        }
    )
    print("Chat simples:", response.json())

def example_chat_with_code():
    """Exemplo de chat com código"""
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "Explique este código",
            "provider": "claude",
            "code_content": "def hello():\n    print('Hello, World!')",
            "output_format": "markdown"
        }
    )
    print("Chat com código:", response.json())

def example_chat_with_file():
    """Exemplo de chat com upload de arquivo"""
    with open("example.py", "rb") as f:
        files = {"file": ("example.py", f, "text/plain")}
        data = {
            "message": "Analise este código",
            "provider": "openai",
            "model_type": "smart"
        }
        response = requests.post(
            f"{API_URL}/chat/file",
            data=data,
            files=files
        )
    print("Chat com arquivo:", response.json())

def example_generate_audio():
    """Exemplo de geração de áudio"""
    response = requests.post(
        f"{API_URL}/audio/generate/base64",
        json={
            "text": "Olá, este é um teste de áudio",
            "engine": "openai"
        }
    )
    result = response.json()
    
    # Salva o áudio
    audio_data = base64.b64decode(result["audio_base64"])
    with open("output.mp3", "wb") as f:
        f.write(audio_data)
    print("Áudio salvo como output.mp3")

def example_list_models():
    """Lista modelos disponíveis"""
    response = requests.get(f"{API_URL}/models")
    print("Modelos disponíveis:", json.dumps(response.json(), indent=2))

def example_health_check():
    """Verifica saúde da API"""
    response = requests.get(f"{API_URL}/health")
    print("Status da API:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    # Executa exemplos
    example_health_check()
    example_list_models()
    example_simple_chat()
    example_chat_with_code()
    example_generate_audio()



### Endpoints Principais:

1. **GET /** - Health check básico
2. **GET /health** - Status detalhado da API e providers
3. **GET /models** - Lista todos os modelos disponíveis
4. **POST /chat** - Endpoint principal para chat
5. **POST /chat/file** - Chat com upload de arquivo
6. **POST /audio/generate** - Gera áudio (retorna arquivo)
7. **POST /audio/generate/base64** - Gera áudio (retorna base64)

### Exemplo de uso via cURL:

```bash
# Chat simples
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você está?",
    "provider": "openai",
    "model_type": "fast"
  }'

# Chat com arquivo
curl -X POST "http://localhost:8000/chat/file" \
  -F "message=Analise este código" \
  -F "provider=claude" \
  -F "file=@codigo.py"

# Gerar áudio
curl -X POST "http://localhost:8000/audio/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Olá mundo",
    "engine": "openai"
  }' \
  --output audio.mp3
```

### Documentação Automática:

A API gera documentação automática acessível em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais melhorias:

1. **API RESTful completa** com endpoints bem definidos
2. **Validação automática** usando Pydantic
3. **Documentação automática** com OpenAPI/Swagger
4. **Suporte a upload de arquivos** via multipart/form-data
5. **Respostas em JSON** estruturadas
6. **Tratamento de erros** apropriado com códigos HTTP
7. **Suporte a base64** para PDFs e áudios
8. **Health checks** para monitoramento
9. **Tipagem forte** para melhor manutenibilidade
10. **Async/await** para melhor performance

Para executar a API:

```bash
python api.py
```

Ou com reload automático durante desenvolvimento:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```