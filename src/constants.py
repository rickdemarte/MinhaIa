# Prompts do sistema
#DEFAULT_SYSTEM_PROMPT = """Você é um Analista de TI, atuando como coordenador num setor que presta suporte para toda uma universidade federal. Você é especialista em segurança da informação, LGPD e proteção de dados, além de trabalhar com usuários dos mais diversos tipos. As suas respostas precisam ser cordiais, com baixa profundidade técnica e usar português formal. Porém se a pergunta estiver ao seu alcance, pode responder."""
O_MODEL_SYSTEM_PROMPT = """Você é um especialista em resolução de problemas complexos, análise profunda e programação avançada. Suas respostas devem demonstrar raciocínio estruturado, considerando múltiplas perspectivas e fornecendo soluções detalhadas. Para questões de código, forneça implementações otimizadas e bem documentadas."""
DEFAULT_SYSTEM_PROMPT = O_MODEL_SYSTEM_PROMPT

# PERSONALITY PARA GERAR APENAS O CÓDIGO sem explicações
CODE_GENERATOR = """Você é um gerador de código. Sua tarefa é fornecer apenas o código necessário para resolver o problema apresentado, sem explicações ou comentários adicionais. Foque em entregar soluções eficientes e diretas."""

# Configurações de áudio
DEFAULT_VOICE = "alloy"
#DEFAULT_TTS_MODEL = "gpt-4o-audio-preview"
DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"
#DEFAULT_TTS_MODEL = "tts-1"
#DEFAULT_TTS_MODEL = "tts-1-hd"
DEFAULT_AUDIO_FILE = "voz.mp3"
VOICE_INSTRUCTIONS = "Você é um professor que fala clara e pausadamente"

# Constantes para AWS Polly
DEFAULT_VOICE_ID = "Vitoria"  # Voz brasileira feminina
DEFAULT_ENGINE = "neural"  # 'standard' ou 'neural'
DEFAULT_OUTPUT_FORMAT = "mp3"
DEFAULT_SAMPLE_RATE = "24000"
DEFAULT_LANGUAGE_CODE = "pt-BR"

# Mapeamento de vozes por idioma
VOICE_MAPPING = {
    "pt-BR": {
        "female": ["Camila", "Vitoria"],
        "male": ["Ricardo", "Thiago"]
    },
    "en-US": {
        "female": ["Joanna", "Kendra", "Kimberly", "Salli", "Joey", "Ivy"],
        "male": ["Matthew", "Justin", "Kevin"]
    }
}
