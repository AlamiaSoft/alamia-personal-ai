from abc import ABC, abstractmethod
from typing import List, Dict
from ..schemas.model import ModelProfile

class ModelProvider(ABC):
    """
    Abstract interface for model providers (e.g., Ollama, Groq, OpenRouter).
    """
    
    @abstractmethod
    def discover(self) -> bool:
        """Checks if the provider is reachable and configured."""
        pass
        
    @abstractmethod
    def get_models(self) -> List[ModelProfile]:
        """Fetches and maps available models to AgentHost ModelProfiles."""
        pass
        
    @abstractmethod
    def health(self) -> bool:
        """Verifies health of the provider API."""
        pass
        
    @abstractmethod
    def limits(self) -> Dict[str, any]:
        """Returns rate limits, quotas, and economics."""
        pass
