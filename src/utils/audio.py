import os
import sys
import re
from pathlib import Path
from constants import DEFAULT_VOICE, DEFAULT_TTS_MODEL, VOICE_INSTRUCTIONS

def limpar_texto_para_audio(texto):
    """Remove caracteres desnecessários e formata texto para TTS"""
    # Remove múltiplas quebras de linha
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    # Remove espaços no início e fim das linhas
    texto = '\n'.join(line.strip() for line in texto.split('\n'))
    
    # Remove marcações markdown comuns
    # Headers
    texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
    
    # Bold e itálico
    texto = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', texto)  # Bold + itálico
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)      # Bold
    texto = re.sub(r'\*(.*?)\*', r'\1', texto)          # Itálico
    texto = re.sub(r'__(.*?)__', r'\1', texto)          # Bold alternativo
    texto = re.sub(r'_(.*?)_', r'\1', texto)            # Itálico alternativo
    
    # Remove código inline e blocos de código
    texto = re.sub(r'```[^`]*```', '', texto, flags=re.DOTALL)
    texto = re.sub(r'`([^`]+)`', r'\1', texto)
    
    # Remove links mas mantém o texto
    texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)
    
    # Remove URLs
    texto = re.sub(r'https?://\S+', '', texto)
    
    # Remove caracteres especiais de markdown
    texto = re.sub(r'^[\*\-\+]\s+', '', texto, flags=re.MULTILINE)  # Listas
    texto = re.sub(r'^\d+\.\s+', '', texto, flags=re.MULTILINE)     # Listas numeradas
    texto = re.sub(r'^>\s+', '', texto, flags=re.MULTILINE)         # Citações
    texto = re.sub(r'\|', ' ', texto)                               # Tabelas
    
    # Remove emojis e caracteres especiais
    texto = re.sub(r'[^\w\s\.,;:!?\-áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]', ' ', texto)
    
    # Remove múltiplos espaços
    texto = re.sub(r'\s+', ' ', texto)
    
    # Remove espaços antes de pontuação
    texto = re.sub(r'\s+([.,;:!?])', r'\1', texto)
    
    # Garante espaço após pontuação
    texto = re.sub(r'([.,;:!?])(\w)', r'\1 \2', texto)
    
    # Remove linhas vazias excessivas
    texto = re.sub(r'\n\s*\n', '\n', texto)
    
    return texto.strip()

def dividir_texto_inteligente(texto, limite=3500):
    """
    Divide o texto em partes menores de forma inteligente,
    tentando não quebrar frases no meio
    """
    if len(texto) <= limite:
        return [texto]
    
    partes = []
    texto_restante = texto
    
    while texto_restante:
        if len(texto_restante) <= limite:
            partes.append(texto_restante)
            break
        
        # Encontra um ponto de corte adequado
        corte = limite
        
        # Tenta cortar em um parágrafo (duas quebras de linha)
        pos_paragrafo = texto_restante.rfind('\n\n', 0, limite)
        if pos_paragrafo > limite * 0.7:  # Se encontrou um parágrafo após 70% do limite
            corte = pos_paragrafo
        else:
            # Tenta cortar em uma quebra de linha simples
            pos_linha = texto_restante.rfind('\n', 0, limite)
            if pos_linha > limite * 0.7:
                corte = pos_linha
            else:
                # Tenta cortar em uma frase (ponto final)
                pos_frase = max(
                    texto_restante.rfind('. ', 0, limite),
                    texto_restante.rfind('! ', 0, limite),
                    texto_restante.rfind('? ', 0, limite)
                )
                if pos_frase > limite * 0.7:
                    corte = pos_frase + 1  # Inclui o ponto
                else:
                    # Tenta cortar em vírgula ou ponto e vírgula
                    pos_virgula = max(
                        texto_restante.rfind(', ', 0, limite),
                        texto_restante.rfind('; ', 0, limite)
                    )
                    if pos_virgula > limite * 0.7:
                        corte = pos_virgula + 1
                    else:
                        # Último recurso: corta em espaço
                        pos_espaco = texto_restante.rfind(' ', 0, limite)
                        if pos_espaco > 0:
                            corte = pos_espaco
        
        # Adiciona a parte e continua com o resto
        partes.append(texto_restante[:corte].strip())
        texto_restante = texto_restante[corte:].strip()
    
    return partes

def gerar_audio_openai(texto, nome_arquivo="voz.mp3", modelo=DEFAULT_TTS_MODEL, voz=DEFAULT_VOICE, persona=VOICE_INSTRUCTIONS):
    """Gera arquivo(s) MP3 com a resposta usando TTS da OpenAI"""
    try:
        from openai import OpenAI
    except ImportError:
        print("Erro: Funcionalidade de voz requer biblioteca OpenAI", file=sys.stderr)
        sys.exit(1)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Erro: Variável de ambiente OPENAI_API_KEY não encontrada", file=sys.stderr)
        sys.exit(1)
    
    # Limpa o texto antes de processar
    texto_limpo = limpar_texto_para_audio(texto)
    
    if not texto_limpo:
        print("Erro: Texto vazio após limpeza", file=sys.stderr)
        sys.exit(1)
    
    # Divide o texto se necessário
    partes = dividir_texto_inteligente(texto_limpo, limite=3500)
    
    if len(partes) == 1:
        # Texto cabe em um único arquivo
        print(f"[📝] Texto preparado para áudio ({len(texto_limpo)} caracteres)", file=sys.stderr)
        _gerar_audio_parte(texto_limpo, nome_arquivo, modelo, voz, persona, api_key)
    else:
        # Texto precisa ser dividido
        print(f"[📝] Texto muito grande ({len(texto_limpo)} caracteres)", file=sys.stderr)
        print(f"[✂️] Dividindo em {len(partes)} partes", file=sys.stderr)
        
        # Extrai nome base e extensão
        path = Path(nome_arquivo)
        nome_base = path.stem
        extensao = path.suffix or '.mp3'
        diretorio = path.parent
        
        arquivos_gerados = []
        
        for i, parte in enumerate(partes, 1):
            nome_parte = diretorio / f"{nome_base}_parte{i}{extensao}"
            print(f"\n[🎯] Gerando parte {i}/{len(partes)} ({len(parte)} caracteres)", file=sys.stderr)
            _gerar_audio_parte(parte, str(nome_parte), modelo, voz, persona, api_key)
            arquivos_gerados.append(str(nome_parte))
        
        print(f"\n[✓] Áudio dividido em {len(partes)} arquivos:", file=sys.stderr)
        for arquivo in arquivos_gerados:
            print(f"    - {arquivo}", file=sys.stderr)
        
        # Cria arquivo de informações
        info_file = diretorio / f"{nome_base}_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"Áudio dividido em {len(partes)} partes:\n\n")
            for i, arquivo in enumerate(arquivos_gerados, 1):
                f.write(f"Parte {i}: {arquivo}\n")
            f.write(f"\nTamanho total do texto: {len(texto_limpo)} caracteres\n")
            f.write(f"Gerado em: {os.path.basename(sys.argv[0])}\n")
        
        print(f"[📄] Informações salvas em: {info_file}", file=sys.stderr)

def _gerar_audio_parte(texto, nome_arquivo, modelo, voz, persona, api_key):
    """Função auxiliar para gerar uma parte do áudio"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.audio.speech.create(
            model=modelo,
            voice=voz,
            instructions=persona,
            input=texto
        )
        response.stream_to_file(nome_arquivo)
        print(f"[✓] Áudio salvo: {nome_arquivo}", file=sys.stderr)
    except Exception as e:
        print(f"[✗] Erro ao gerar áudio: {e}", file=sys.stderr)
        sys.exit(1)