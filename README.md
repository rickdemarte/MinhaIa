# AI CLI - Cliente Unificado para APIs de IA

## Descrição do Projeto
AI CLI é um cliente unificado que permite a interação com várias APIs de inteligência artificial (IA) através de uma interface de linha de comando (CLI). Este projeto fornece uma maneira fácil e eficiente de acessar diferentes provedores de IA, como OpenAI, Anthropic, DeepSeek, Qwen e Grok, usando um único comando. Com o AI CLI, os usuários podem gerar respostas, realizar análises de documentos, gerar áudio e muito mais, tudo a partir de um terminal.

## Funcionalidades
- **Interação com múltiplos provedores**: Você pode escolher qual provedora de IA utilizar através de argumentos de linha de comando.
- **Versatilidade de Comandos**: Execute uma ampla gama de funções, como gerar texto, analisar código, ler PDFs e formatar respostas.
- **Configuração de modelos**: O cliente permite selecionar diferentes modelos de IA com base em suas necessidades (rápido, barato, inteligente, etc.).
- **Personalidade da IA**: Defina a personalidade da IA para adaptar as respostas ao seu contexto.
- **Geração de áudio**: Converta texto em áudio MP3 usando serviços como OpenAI e Amazon Polly, gerando áudio a partir das respostas.
- **Processamento de texto**: Suporta o envio de mensagens diretamente ou através de arquivos de texto, PDF e código.
- **Verificação e instalação de dependências**: Um comando para verificar se todas as dependências necessárias estão instaladas e configuradas corretamente.

## Estrutura do Projeto
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

## Requisitos
- Python 3.6 ou superior
- Dependências específicas para cada provedor de IA (certifique-se de instalá-las conforme necessário).

## Como Usar
Para utilizar o AI CLI, você pode executar o comando `chat` seguido de um texto e opções específicas. Aqui estão alguns exemplos de uso:

1. **Clone o repositório**:
   ```bash
   git clone git@github.com:rickdemarte/MinhaIa MinhaIa
   cd MinhaIa
   ```

2. **Execute o script de configuração**:
   ```bash
   ./chat --setup
   ```

   **Recomendo usar a extensão -force para forçar a instalação das dependências**
   ```bash
   # Adiciona --break-system-packages ao instalar as dependências em Python
   ./chat --setup-force
   ```

   **Execute a verificação de dependências**
   ```bash
   ./chat --check-deps
   ```
   
   **Essenciais**

   [ ] openai - Se usar ChatGPT e Qwen
   [ ] anthropic - Se usar Claude
   [ ] xai_sdk - Se usar Grok
   [ ] pdfplumber - Para lidar com PDF's
   [ ] boto3 - Pra usar Polly da AWS

3. **(Se necessário) Instale as dependências**:

   Não é necessário se rodar o -setup, pois ao final da função, '--install-deps' é chamado automaticamente
   ```bash
   ./chat --install-deps
   ```
   **Recomendo usar a extensão -force para forçar a instalação das dependências**
   ```bash
   # Adiciona --break-system-packages
   ./chat --install-deps-force
   ```

4. **Configure suas variáveis de ambiente**:
   As seguintes variáveis de ambiente são necessárias para usar as APIs:
   - `OPENAI_API_KEY`: Chave da API OpenAI.
   - `ANTHROPIC_API_KEY`: Chave da API Anthropic.
   - `DEEPSEEK_API_KEY`: Chave da API DeepSeek.
   - `QWEN_API_KEY`: Chave da API Qwen.
   - `GROK_API_KEY`: Chave da API Grok.

5. **Execute o cliente**:
   ```bash
   ./chat --provider <provedor> "sua mensagem aqui"
   ```

   **Exemplo**:
   ```bash
   ./chat --provider openai "Qual é a capital da França?"
   ```

### Argumentos de Linha de Comando
- `mensagem`: Texto a ser enviado para o provedor.
- `--provider [openai|claude|deepseek|qwen|grok]`: Escolha o provedor (padrão: openai).
- `--fast`, `--cheap`, `--smart`, `--smartest`, `--absurdo`: Seleciona o modelo desejado.
- `-t`: Remove markdown da resposta.
- `-f`: Salva a resposta em um arquivo.
- `-p`: Formata a resposta como log.
- `--voz`: Gera áudio da resposta usando OpenAI.
- `--polly`: Gera áudio da resposta usando Amazon Polly.
- `--codigo ARQUIVO`: Analisa um arquivo de código.
- `--pdf ARQUIVO`: Analisa um arquivo PDF.
- `--code LINGUAGEM`: Gera um código puro, sem explicações
- `--persona PERSONALIDADE`: Define uma personalidade a ser usada pela IA

### Exemplos de Uso
Para enviar um arquivo PDF e obter uma resposta:
```bash
./chat --provider openai --pdf seu_arquivo.pdf
```

Para executar um comando específico:
```bash
chat "Explique firewall"
chat "O que é LGPD?" --provider claude --smart
chat "Analise este código" --codigo script.py --smartest
chat "Resuma" --pdf documento.pdf -f resumo.txt
```

## Contribuição
Contribuições são bem-vindas! Se você gostaria de contribuir com o projeto, sinta-se à vontade para abrir um pull request ou relatar um problema no repositório.

