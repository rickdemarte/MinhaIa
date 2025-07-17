# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
AI CLI (MinhaIa) is a unified command-line interface for interacting with multiple AI APIs including OpenAI, Anthropic, DeepSeek, Qwen, and Grok. The project provides a single entry point (`./chat`) to access different AI providers with various models and capabilities.

## Development Commands

### Primary Usage
```bash
# Basic usage
./chat "your message here"

# With specific provider and model
./chat --provider claude --smart "your message"

# Process files
./chat --codigo script.py "analyze this code"
./chat --pdf document.pdf "summarize this"
./chat --texto file.txt "read this"
```

### Setup and Installation
```bash
# Initial setup
./chat --setup

# Force setup (overwrites existing)
./chat --setup-force

# Check dependencies
./chat --check-deps

# Install dependencies
./chat --install-deps
./chat --install-deps-force  # with --break-system-packages
```

### Testing and Validation
```bash
# List available models
./chat --list-models

# Test with dry run
./chat --provider dryrun "test message"

# Check system dependencies
./chat --check-deps
```

## Architecture

### Core Components

1. **Entry Point**: `./chat` (bash script) - Main CLI wrapper that handles setup, dependency checking, and calls Python scripts
2. **Main Logic**: `src/main.py` - Central orchestrator that loads configurations and routes requests to appropriate providers
3. **Provider System**: `src/providers/` - Abstract base class with concrete implementations for each AI service
4. **Utilities**: `src/utils/` - Argument parsing, response handling, and formatting
5. **Configuration**: `config/models.json` - Model definitions and capabilities for each provider

### Provider Architecture
All providers inherit from `BaseProvider` (src/providers/base.py) which defines:
- `call_api(message, model, max_tokens, **kwargs)` - Main API call method
- `get_available_models()` - Return available models

Current providers:
- OpenAI (including GPT-4, GPT-4o, o3-mini, o3)
- Anthropic (Claude variants)
- DeepSeek (chat and reasoner models)
- Qwen/Alibaba (multiple model tiers)
- Grok (X/Twitter AI)
- AWS Transcribe (audio transcription)
- OpenAI Whisper (audio transcription)

### Model Configuration System
Models are defined in `config/models.json` with tiers:
- `fast/cheap`: Quick, economical models
- `smart`: Balanced performance
- `smartest`: Most capable models
- `absurdo`: Maximum power (OpenAI o3 only)

Each model configuration includes:
- Model name/ID
- Max tokens
- Description
- Special flags (e.g., `is_o_model` for reasoning models)

### File Processing
The system supports multiple input formats:
- Code files (`--codigo`) - Direct file reading
- PDF files (`--pdf`) - Text extraction using pdfplumber
- Text files (`--texto`) - Plain text processing
- Audio files (`--transcribe`) - Speech-to-text via AWS Transcribe or OpenAI Whisper

### Audio Features
- Text-to-speech: OpenAI TTS or AWS Polly
- Speech-to-text: AWS Transcribe or OpenAI Whisper
- Audio playback: Built-in playback support

## Required Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
QWEN_API_KEY=your_qwen_key
GROK_API_KEY=your_grok_key
```

AWS credentials should be configured via:
- `~/.aws/credentials` file
- AWS CLI (`aws configure`)

## Dependencies
Core Python packages (see requirements.txt):
- `openai==1.93.0` - OpenAI API client
- `anthropic==0.54.0` - Anthropic API client
- `pdfplumber==0.11.7` - PDF text extraction
- `boto3==1.39.3` - AWS services
- `xai_sdk` - Grok API client
- `pydub` - Audio processing

## Common Development Tasks

### Adding a New Provider
1. Create new provider class in `src/providers/` inheriting from `BaseProvider`
2. Implement `call_api()` and `get_available_models()` methods
3. Add provider to `config/models.json` with model configurations
4. Update argument parser in `src/utils/argumentos.py`
5. Add provider initialization in `src/main.py`

### Modifying Model Configurations
Edit `config/models.json` to add/modify model definitions. Each provider should have:
- `default`: Fallback model
- `fast/cheap`: Economical options
- `smart`: Balanced performance
- `smartest`: Most capable option

### Error Handling
- All file operations include proper error handling with user-friendly messages
- API errors are caught and displayed with context
- Dependency checking validates required libraries and environment variables

### Audio Processing
- TTS providers return audio file paths for chaining with playback
- Transcription providers handle various audio formats
- Audio playback uses system `mpg123` command

## Testing
Test files are located in `tests/` directory and include:
- Sample audio files (.mp3)
- Test documents (.pdf, .md, .txt)
- Example code files

Use `--provider dryrun` for testing argument parsing without API calls.