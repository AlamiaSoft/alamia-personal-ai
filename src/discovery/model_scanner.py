import os
from typing import List
from .providers.ollama import OllamaProviderAdapter
from .providers.groq import GroqProviderAdapter
from .providers.openai import OpenAIProviderAdapter
from .providers.anthropic import AnthropicProviderAdapter
from .providers.openrouter import OpenRouterProviderAdapter
from ..capabilities.probe_engine import CapabilityProbeEngine
from ..domain.schemas.model import ModelProfile
from ..domain.errors import DiscoveryError

class ModelScanner:
    def __init__(self, ollama_host: str = "http://127.0.0.1:11434"):
        self.providers = [
            OllamaProviderAdapter(host=ollama_host),
            GroqProviderAdapter(),
            OpenAIProviderAdapter(),
            AnthropicProviderAdapter(),
            OpenRouterProviderAdapter()
        ]
        self.probe_engine = CapabilityProbeEngine()

    def scan_ollama(self) -> List[ModelProfile]:
        adapter = OllamaProviderAdapter(host=self.ollama_host)
        return [self.probe_engine.enrich_model_profile(m) for m in adapter.discover_models()]

    def scan_cloud(self) -> List[ModelProfile]:
        cloud_adapters = [a for a in self.providers if not isinstance(a, OllamaProviderAdapter)]
        models = []
        for adapter in cloud_adapters:
            models.extend(adapter.discover_models())
        return [self.probe_engine.enrich_model_profile(m) for m in models]

    def scan_all(self) -> List[ModelProfile]:
        """
        Scans all configured providers for actually available models,
        and enriches them with empirical capability evidence.
        """
        discovered_models: List[ModelProfile] = []
        
        try:
            for adapter in self.providers:
                models = adapter.discover_models()
                for m in models:
                    # Enrich with empirical evidence if present; unprobed stay UNKNOWN (conf=0.0)
                    enriched = self.probe_engine.enrich_model_profile(m)
                    discovered_models.append(enriched)

            return discovered_models
        except Exception as e:
            raise DiscoveryError(f"Failed to scan models: {str(e)}")
