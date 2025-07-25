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
/
├── chat [Aplicativo em bash]
├── docs
│   ├── SECURE_ERROR_HANDLING.md
│   ├── CLAUDE.md
│   └── ...
├── requirements.txt
├── config
│   ├── models.json
│   └── ...
├── tests [arquivos de teste, não soncronizados]
├── src
│   ├── utils
│   │   ├── error_handler.py
│   │   ├── formatters.py
│   │   ├── argumentos.py
│   │   ├── handlers.py
│   │   └── ...
│   ├── providers
│   │   ├── deepseek_provider.py
│   │   ├── base.py
│   │   ├── openaiTTS_provider.py
│   │   ├── openaiWhisper_provider.py
│   │   ├── openai_provider.py
│   │   ├── groq_provider.py
│   │   ├── factory.py
│   │   ├── AWSpolly_provider.py
│   │   ├── alibaba_provider.py
│   │   ├── grok_provider.py
│   │   ├── claude_provider.py
│   │   ├── groqTTS_provider.py
│   │   ├── AWStranscribe_provider.py
│   │   └── ...
│   ├── processors
│   │   ├── message_processor.py
│   │   └── ...
│   ├── constants.py
│   ├── main.py
│   ├── config
│   │   ├── manager.py
│   │   └── ...
│   └── ...
├── README.md
└── 
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

   **Recomendo usar a extensão -force para forçar a instação das dependências**
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
   **Recomendo usar a extensão -force para forçar a instação das dependências**
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
   - `GROQ_API_KEY`: Chave da API Groq.

5. **Execute o cliente**:
   ```bash
   ./chat --provider <provedor> "sua mensagem aqui"
   ```

   **Exemplo**:
   ```bash
   ./chat --provider openai "Qual é a capital da França?"
   ```

### Argumentos de Linha de Comando

```
USO:
    chat "texto" [opções]

OPÇÕES PRINCIPAIS:
    --provider [openai|claude|deepseek|qwen|grok]  Escolhe o provider (padrão: openai)
    --help, -h                  Mostra esta ajuda
    --version                   Mostra a versão
    --list-models               Lista modelos disponíveis

OPÇÕES DE CONFIGURAÇÃO / INSTALAÇÃO:
    --setup [LOCAL]             Cria estrutura inicial do projeto
    --setup-force [LOCAL]       Cria estrutura inicial do projeto (força instalação removendo diretório existente e forçando instalação de dependências)
    --check-deps                Verifica dependências do sistema
    --install-deps              Instala dependências Python
    --install-deps-force        Instala dependências Python (forçado usando --break-system-packages)

OPÇÕES DE PROVIDER:
    --openai                    Usa OpenAI (padrão)
    --anthropic                 Usa Anthropic
    --deepseek                  Usa DeepSeek
    --qwen                      Usa Qwen
    --grok                      Usa Grok
    --groq                      Usa Groq

OPÇÕES DE PERSONALIDADE:
    --persona NOME              Define a personalidade da IA (ex: --persona "engenheiro de software")
    --code LINGUAGEM            Gera código sem explicações

OPÇÕES DE MODELO:
    --fast                      Modelo rápido e econômico
    --smart                     Modelo equilibrado
    --smartest                  Modelo mais inteligente
    --absurdo                   Máximo poder (apenas OpenAI)
    --model NOME                Especifica modelo customizado

OPÇÕES DE FORMATAÇÃO:
    -t                          Remove markdown da resposta
    -f ARQUIVO                  Salva resposta em arquivo
    -p                          Formata como log do sistema

OPÇÕES DE VOZ:
    --voz [ARQUIVO]             Gera áudio MP3 (apenas OpenAI)
    --voz [ARQUIVO] --groq      Gera áudio MP3 usando Groq (playai-tts)
    --polly [ARQUIVO]           Gera áudio MP3 usando Amazon Polly
    --ouvir                     Reproduz áudio MP3 gerado
    --transcribe [ARQUIVO]      Transcreve áudio MP3 para texto

OPÇÕES DE ENTRADA:
    --codigo ARQUIVO            Analisa arquivo de código
    --pdf ARQUIVO               Analisa arquivo PDF
    --texto ARQUIVO             Lê texto de arquivo

EXEMPLOS:
    chat "Explique firewall"
    chat "O que é LGPD?" --provider claude --smart
    chat "Analise este código" --codigo script.py --smartest
    chat "Resuma" --pdf documento.pdf -f resumo.txt

VARIÁVEIS DE AMBIENTE:
    OPENAI_API_KEY              Chave da API OpenAI
    ANTHROPIC_API_KEY           Chave da API Anthropic
    DEEPSEEK_API_KEY            Chave da API DeepSeek
    QWEN_API_KEY                Chave da API Qwen
    GROK_API_KEY                Chave da API Grok
    GROQ_API_KEY                Chave da API Groq

```

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

