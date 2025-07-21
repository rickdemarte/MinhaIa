import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple


class ConfigManager:
    """Manages configuration loading and model selection"""
    
    def __init__(self):
        self._models_config = None
        self._config_path = Path(__file__).parent.parent.parent / "config" / "models.json"
    
    def load_models_config(self) -> Dict[str, Any]:
        """Load models configuration from JSON file"""
        if self._models_config is None:
            try:
                with open(self._config_path, 'r') as f:
                    self._models_config = json.load(f)
            except FileNotFoundError:
                print(f"Erro: Arquivo de configuração não encontrado: {self._config_path}", file=sys.stderr)
                sys.exit(1)
        return self._models_config
    
    def get_model_config(self, args, provider: str) -> Tuple[str, int, bool]:
        """Determine which model to use based on arguments"""
        models_config = self.load_models_config()
        print(f"Usando provider: {provider}", file=sys.stderr)
        
        provider_models = models_config[provider]['models']
        
        # Handle transcription
        if args.transcribe:
            if provider not in ['openai', 'whisper']:
                return provider_models['transcribe']['bucket_name'], 0, False
        
        # Handle model tier selection
        if args.fast and 'fast' in provider_models:
            config = provider_models['fast']
        elif args.cheap and 'cheap' in provider_models:
            config = provider_models['cheap']
        elif args.smart and 'smart' in provider_models:
            config = provider_models['smart']
        elif args.smartest and 'smartest' in provider_models:
            config = provider_models['smartest']
        elif args.absurdo and provider == 'groq' and 'absurdo' in provider_models:
            config = provider_models['absurdo']
        elif args.absurdo and provider == 'openai' and 'absurdo' in provider_models:
            config = provider_models['absurdo']
        elif args.model:
            # Custom model
            return args.model, 4096, False
        else:
            config = provider_models['default']
        
        return config['model'], config['max_tokens'], config.get('is_o_model', False)
    
    def list_available_models(self) -> None:
        """Print all available models"""
        models_config = self.load_models_config()
        print("\n=== Modelos Disponíveis ===")
        for provider, config in models_config.items():
            print(f"\n{provider.upper()}:")
            for alias, model_config in config['models'].items():
                print(f"  {alias}: {model_config['model']} ({model_config['description']})")