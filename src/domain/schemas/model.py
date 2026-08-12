from pydantic import BaseModel, Field
from typing import Optional, Literal

ProvenanceType = Literal["runtime_metadata", "provider_metadata", "empirical", "estimated", "unknown"]

class ProviderInfo(BaseModel):
    id: str
    type: str  # e.g., "local", "cloud"

class HardwareRequirements(BaseModel):
    vram_required_gb: Optional[float] = None
    ram_required_gb: Optional[float] = None
    is_estimated: bool = True

class Capabilities(BaseModel):
    coding: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: float = Field(default=0.0, ge=0.0, le=1.0)
    tool_calling: float = Field(default=0.0, ge=0.0, le=1.0)
    vision: float = Field(default=0.0, ge=0.0, le=1.0)

class Context(BaseModel):
    window: Optional[int] = None  # None represents UNKNOWN context window

class Economics(BaseModel):
    cost_per_1m_input: Optional[float] = None
    cost_per_1m_output: Optional[float] = None

class Limits(BaseModel):
    tpm: Optional[int] = None

class Evidence(BaseModel):
    source: ProvenanceType = "unknown"
    tested: bool = False
    test_suite: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class ModelProfile(BaseModel):
    id: str
    digest: Optional[str] = None
    provider: ProviderInfo
    hardware: HardwareRequirements
    capabilities: Capabilities
    context: Context
    economics: Economics
    limits: Limits
    evidence: Evidence
