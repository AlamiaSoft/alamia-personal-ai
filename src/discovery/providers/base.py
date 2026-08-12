from abc import ABC, abstractmethod
from typing import List
from ...domain.schemas.model import ModelProfile

class BaseProviderAdapter(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Returns the unique identifier for this provider adapter."""
        pass

    @abstractmethod
    def discover_models(self) -> List[ModelProfile]:
        """Discovers and returns list of ModelProfile instances from provider."""
        pass
