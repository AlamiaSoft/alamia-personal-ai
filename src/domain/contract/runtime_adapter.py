from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ..schemas.model import ModelProfile
from ..schemas.execution import ExecutionProfile

class RuntimeInfo(BaseModel):
    version: str
    is_installed: bool
    status: str

class InstallResult(BaseModel):
    success: bool
    logs: str

class RuntimeConfig(BaseModel):
    presets: Dict[str, Any]
    env: Dict[str, str]

class HealthStatus(BaseModel):
    is_healthy: bool
    message: str

class CapabilitySet(BaseModel):
    supported_features: List[str]

class ModelList(BaseModel):
    models: List[ModelProfile]

class ExecuteRequest(BaseModel):
    context_id: str
    message: str
    attachments: List[Any] = []

class ExecuteResult(BaseModel):
    success: bool
    response: str

class EventStream:
    # A placeholder for an async generator or stream interface
    pass

class Journal(BaseModel):
    logs: List[str]

class Diagnostics(BaseModel):
    metrics: Dict[str, Any]

class RuntimeAdapter(ABC):
    """Abstract contract for AgentHost runtime adapters."""
    
    @abstractmethod
    def discover(self) -> RuntimeInfo:
        pass
        
    @abstractmethod
    def install(self) -> InstallResult:
        pass
        
    @abstractmethod
    def configure(self, cfg: RuntimeConfig) -> None:
        pass
        
    @abstractmethod
    def start(self) -> None:
        pass
        
    @abstractmethod
    def stop(self) -> None:
        pass
        
    @abstractmethod
    def restart(self) -> None:
        pass
        
    @abstractmethod
    def health(self) -> HealthStatus:
        pass
        
    @abstractmethod
    def capabilities(self) -> CapabilitySet:
        pass
        
    @abstractmethod
    def models(self) -> ModelList:
        pass
        
    @abstractmethod
    def execute(self, req: ExecuteRequest) -> ExecuteResult:
        pass
        
    @abstractmethod
    def stream(self, req: ExecuteRequest) -> EventStream:
        pass
        
    @abstractmethod
    def cancel(self, ctx_id: str) -> None:
        pass
        
    @abstractmethod
    def logs(self, ctx_id: str) -> Journal:
        pass
        
    @abstractmethod
    def diagnostics(self) -> Diagnostics:
        pass
