from abc import ABC, abstractmethod
from typing import List
from ...domain.schemas.model import ModelProfile

class BaseProviderAdapter(ABC):
    @abstractmethod
    def discover_models(self) -> List[ModelProfile]:
        """Discovers and returns list of ModelProfile instances from provider."""
        pass
