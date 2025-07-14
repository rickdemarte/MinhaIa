# README

## Cliente Unificado para APIs de IA

Este projeto é um cliente unificado para diferentes APIs de Inteligência Artificial. Ele permite que usuários interajam com diversos provedores de serviços de IA, como OpenAI, Claude, DeepSeek, Alibaba (Qwen), e Grok, através de uma interface de linha de comando (CLI) simples e intuitiva.

### Funcionalidades

- **Interação com múltiplos provedores**: Você pode escolher qual provedora de IA utilizar através de argumentos de linha de comando.
- **Configuração de modelos**: O cliente permite selecionar diferentes modelos de IA com base em suas necessidades (rápido, barato, inteligente, etc.).
- **Processamento de texto**: Suporta o envio de mensagens diretamente ou através de arquivos de texto, PDF e código.
- **Geração de áudio**: É possível gerar áudio a partir das respostas utilizando a API da OpenAI ou Amazon Polly.
- **Formatação de resposta**: O cliente pode formatar a resposta em log ou salvar o resultado em um arquivo.
- **Suporte a personalidades**: Permite definir uma personalidade para a IA, personalizando ainda mais as interações.

### Requisitos

- Python 3.6 ou superior
- Dependências específicas para cada provedor de IA (certifique-se de instalá-las conforme necessário).

### Estrutura do Projeto

```
│
├── src
│   ├── providers
│   │   ├── openai_provider.py
│   │   ├── claude_provider.py
│   │   ├── deepseek_provider.py
│   │   ├── alibaba_provider.py
│   │   └── grok_provider.py
│   ├── utils
│   │   ├── formatters.py
│   │   ├── file_handlers.py
│   │   └── audio.py
│   └── main.py
└── config
    └── models.json
```

### Como Usar

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu_usuario/seu_repositorio.git
   cd seu_repositorio
   ```

2. **Instale as dependências** (se necessário).

3. **Execute o cliente**:
   ```bash
   python src/main.py --provider <provedor> --mensagem "sua mensagem aqui"
   ```

   **Exemplo**:
   ```bash
   python src/main.py --provider openai --mensagem "Qual é a capital da França?"
   ```

### Argumentos de Linha de Comando

- `mensagem`: Texto a ser enviado para o provedor.
- `--provider`: Escolha entre `openai`, `claude`, `deepseek`, `qwen`, e `grok`.
- `--fast`, `--cheap`, `--smart`, `--smartest`, `--absurdo`: Seleciona o modelo desejado.
- `-t`: Remove markdown da resposta.
- `-f`: Salva a resposta em um arquivo.
- `-p`: Formata a resposta como log.
- `--voz`: Gera áudio da resposta usando OpenAI.
- `--polly`: Gera áudio da resposta usando Amazon Polly.
- `--codigo`: Processa arquivos de código.
- `--pdf`: Processa arquivos PDF para obter conteúdo.

### Exemplo de Uso com Arquivo

Para enviar um arquivo PDF e obter uma resposta:
```bash
python src/main.py --provider openai --pdf seu_arquivo.pdf
```

### Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades. Faça um fork do repositório e envie um pull request com suas alterações.

### Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Conclusão

Este cliente unificado para APIs de IA oferece uma maneira fácil e eficiente de interagir com diversos provedores de inteligência artificial, permitindo que você aproveite o poder da IA em suas aplicações.