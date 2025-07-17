# Secure Error Handling Guide

This guide explains how to implement secure error handling across all providers to prevent information disclosure.

## Overview

The `SecureErrorHandler` class provides centralized error handling that:
- Logs detailed error information for debugging
- Shows only sanitized messages to users
- Prevents sensitive data exposure
- Provides helpful hints without revealing system details

## Implementation Steps

### 1. Import the Error Handler

Add to your provider imports:
```python
from utils.error_handler import SecureErrorHandler
```

### 2. Replace Error Messages

#### API Key Errors
Before:
```python
print("Erro: Variável de ambiente OPENAI_API_KEY não encontrada", file=sys.stderr)
sys.exit(1)
```

After:
```python
SecureErrorHandler.handle_error(
    "api_key_missing",
    Exception("OPENAI_API_KEY not found"),
    context={"provider": "openai"}
)
```

#### API Communication Errors
Before:
```python
print(f"Erro na chamada da API: {e}", file=sys.stderr)
sys.exit(1)
```

After:
```python
SecureErrorHandler.handle_error(
    "api_error",
    e,
    context={"provider": "provider_name", "model": model}
)
```

#### File Not Found Errors
Before:
```python
print(f"Erro: Arquivo '{file_path}' não encontrado", file=sys.stderr)
```

After:
```python
SecureErrorHandler.handle_error(
    "file_not_found",
    FileNotFoundError(f"File not found: {SecureErrorHandler.sanitize_path(file_path)}"),
    context={"provider": "provider_name"}
)
```

#### Network Errors
Before:
```python
print(f"Erro de conexão: {e}", file=sys.stderr)
```

After:
```python
SecureErrorHandler.handle_error(
    "network_error",
    e,
    context={"provider": "provider_name"}
)
```

### 3. Error Types

Available error types:
- `api_key_missing` - Missing API credentials
- `api_error` - General API errors
- `file_not_found` - File not found
- `permission_denied` - Permission issues
- `invalid_input` - Invalid user input
- `dependency_missing` - Missing library
- `network_error` - Network connectivity
- `rate_limit` - API rate limiting
- `invalid_format` - Invalid file format
- `generic` - Other errors

### 4. Best Practices

1. **Never expose sensitive data** in error messages:
   - API keys or tokens
   - Full file paths
   - System information
   - Stack traces
   - Raw API responses

2. **Use context for logging**:
   ```python
   context={
       "provider": "provider_name",
       "model": model,
       "operation": "transcription"
   }
   ```

3. **Sanitize paths and URLs**:
   ```python
   SecureErrorHandler.sanitize_path(file_path)
   SecureErrorHandler.sanitize_url(api_url)
   ```

4. **Control exit behavior**:
   ```python
   # Exit with error code 1 (default)
   SecureErrorHandler.handle_error("api_error", e)
   
   # Don't exit (for recoverable errors)
   SecureErrorHandler.handle_error("api_error", e, exit_code=0)
   ```

5. **Hide hints when not helpful**:
   ```python
   SecureErrorHandler.handle_error(
       "api_error", e, 
       show_hint=False
   )
   ```

## Testing

To test error handling:

1. **Check error messages** don't expose:
   - API endpoints
   - File system structure
   - Internal error details
   - Sensitive configuration

2. **Verify logs** contain full details at:
   ```
   ~/.minhaia/logs/errors_YYYYMMDD.log
   ```

3. **Test each error type**:
   ```bash
   # Missing API key
   unset OPENAI_API_KEY && ./chat "test"
   
   # Invalid file
   ./chat --codigo /nonexistent/file.py "analyze"
   
   # Network error (disconnect internet)
   ./chat "test message"
   ```

## Migration Checklist

For each provider:
- [ ] Import SecureErrorHandler
- [ ] Replace print error statements
- [ ] Add appropriate context
- [ ] Test error scenarios
- [ ] Verify no sensitive data exposed
- [ ] Check logs capture full details

## Example Migration

See the updated providers:
- `openai_provider.py` - Complete example
- `deepseek_provider.py` - API error handling
- `openaiWhisper_provider.py` - File handling errors