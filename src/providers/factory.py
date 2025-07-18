from providers.openai_provider import OpenAIProvider
from providers.claude_provider import ClaudeProvider
from providers.deepseek_provider import DeepSeekProvider
from providers.alibaba_provider import Qwen3Provider
from providers.grok_provider import GrokProvider
from providers.openaiWhisper_provider import WhisperProvider
from providers.AWStranscribe_provider import AWSTranscribeProvider
from providers.groq_provider import GroqProvider



class ProviderFactory:
    """Factory class for creating AI provider instances"""
    
    _providers = {
        'openai': OpenAIProvider,
        'claude': ClaudeProvider,
        'deepseek': DeepSeekProvider,
        'qwen': Qwen3Provider,
        'grok': GrokProvider,
        'whisper': WhisperProvider,
        'aws_transcribe': AWSTranscribeProvider,
        'groq': GroqProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str):
        """Create a provider instance based on the provider name"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        return cls._providers[provider_name]()
    
    @classmethod
    def get_available_providers(cls):
        """Get list of available provider names"""
        return list(cls._providers.keys())