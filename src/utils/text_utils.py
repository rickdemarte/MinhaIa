import re

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
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)  # Bold + itálico
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)      # Bold
    texto = re.sub(r'\*(.*?)\*', r'\1', texto)          # Itálico
    texto = re.sub(r'__(.*?)__', r'\1', texto)          # Bold alternativo
    texto = re.sub(r'_(.*?)_', r'\1', texto)            # Itálico alternativo
    
    # Remove código inline e blocos de código
    texto = re.sub(r'```[^`]*```', '', texto, flags=re.DOTALL)
    texto = re.sub(r'`([^`]+)`', r'\1', texto)
    
    # Remove links mas mantém o texto
    texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)
    
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

def dividir_texto_inteligente(texto, limite=2900):
    """
    Divide o texto em partes menores de forma inteligente,
    tentando não quebrar frases no meio.
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