import sys

def processar_arquivo_codigo(arquivo):
    """Lê e processa um arquivo de código"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        print(f"Erro ao ler o arquivo de código: {e}", file=sys.stderr)
        sys.exit(1)

def processar_arquivo_pdf(arquivo):
    """Lê e processa um arquivo PDF"""
    try:
        import pdfplumber
    except ImportError:
        print("Erro: Biblioteca 'pdfplumber' não instalada. Execute: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)
    
    try:
        with pdfplumber.open(arquivo) as pdf:
            texto_pdf = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    texto_pdf += page_text + '\n'
        
        if not texto_pdf.strip():
            print(f"Aviso: Nenhum texto extraído de {arquivo}.", file=sys.stderr)
        
        return texto_pdf.strip()
    except Exception as e:
        print(f"Erro ao processar o arquivo PDF '{arquivo}': {e}", file=sys.stderr)
        sys.exit(1)