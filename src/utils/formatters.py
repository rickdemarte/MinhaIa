import re
from datetime import datetime

def remove_markdown(text):
    """Remove marcações markdown básicas do texto"""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()

def format_as_log(text, hostname="servidor", provider="ai"):
    """Formata o texto como log do sistema"""
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    lines = text.split('\n')
    return '\n'.join(
        f"{timestamp} {hostname} {provider}[{1000 + i}]: {line.strip()}"
        for i, line in enumerate(lines) if line.strip()
    )