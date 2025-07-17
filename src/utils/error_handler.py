"""
Centralized error handling utility for secure error messages
"""
import sys
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
log_dir = os.path.expanduser("~/.minhaia/logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log"),
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SecureErrorHandler:
    """Handles errors securely by logging detailed info and showing sanitized messages to users"""
    
    # Map of error types to user-friendly messages
    ERROR_MESSAGES = {
        "api_key_missing": "Configuração de autenticação ausente. Verifique as variáveis de ambiente.",
        "api_error": "Erro ao comunicar com o serviço. Tente novamente mais tarde.",
        "file_not_found": "Arquivo solicitado não encontrado.",
        "permission_denied": "Permissão negada para acessar o recurso.",
        "invalid_input": "Entrada inválida fornecida.",
        "dependency_missing": "Dependência do sistema não encontrada.",
        "network_error": "Erro de conexão de rede.",
        "rate_limit": "Limite de requisições excedido. Aguarde antes de tentar novamente.",
        "invalid_format": "Formato de arquivo não suportado.",
        "generic": "Ocorreu um erro inesperado. Consulte os logs para mais detalhes."
    }
    
    @staticmethod
    def handle_error(error_type: str, error: Exception, context: Optional[Dict[str, Any]] = None, 
                    exit_code: int = 1, show_hint: bool = True) -> None:
        """
        Handle errors securely
        
        Args:
            error_type: Type of error from ERROR_MESSAGES keys
            error: The actual exception
            context: Additional context for logging
            exit_code: Exit code for sys.exit (0 to not exit)
            show_hint: Whether to show helpful hints to user
        """
        # Log detailed error information
        logger = logging.getLogger(context.get('provider', 'unknown') if context else 'unknown')
        
        log_context = {
            'error_type': error_type,
            'error_class': error.__class__.__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        logger.error(f"Error occurred: {log_context}", exc_info=True)
        
        # Get user-friendly message
        user_message = SecureErrorHandler.ERROR_MESSAGES.get(
            error_type, 
            SecureErrorHandler.ERROR_MESSAGES['generic']
        )
        
        # Print sanitized error to user
        print(f"Erro: {user_message}", file=sys.stderr)
        
        # Add helpful hints based on error type
        if show_hint:
            hint = SecureErrorHandler._get_hint(error_type, context)
            if hint:
                print(f"Dica: {hint}", file=sys.stderr)
        
        # Add log reference for support
        print(f"Ref: {datetime.now().strftime('%Y%m%d-%H%M%S')}", file=sys.stderr)
        
        if exit_code > 0:
            sys.exit(exit_code)
    
    @staticmethod
    def _get_hint(error_type: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get helpful hints for specific error types"""
        hints = {
            "api_key_missing": {
                "openai": "Execute: export OPENAI_API_KEY='sua_chave_aqui'",
                "claude": "Execute: export ANTHROPIC_API_KEY='sua_chave_aqui'",
                "deepseek": "Execute: export DEEPSEEK_API_KEY='sua_chave_aqui'",
                "qwen": "Execute: export QWEN_API_KEY='sua_chave_aqui'",
                "grok": "Execute: export GROK_API_KEY='sua_chave_aqui'",
                "aws": "Configure AWS com: aws configure"
            },
            "dependency_missing": {
                "openai": "Execute: pip install openai",
                "anthropic": "Execute: pip install anthropic",
                "xai_sdk": "Execute: pip install xai_sdk",
                "pydub": "Execute: pip install pydub",
                "pdfplumber": "Execute: pip install pdfplumber",
                "boto3": "Execute: pip install boto3"
            }
        }
        
        if error_type in hints:
            if isinstance(hints[error_type], dict) and context:
                # Try to get specific hint based on context
                for key, hint in hints[error_type].items():
                    if key in str(context.get('provider', '')).lower():
                        return hint
                    if key in str(context.get('library', '')).lower():
                        return hint
            elif isinstance(hints[error_type], str):
                return hints[error_type]
        
        return None
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """Sanitize file paths for display"""
        # Only show filename, not full path
        return os.path.basename(path)
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitize URLs for display"""
        # Remove query parameters and only show domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"