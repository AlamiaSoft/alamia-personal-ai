from pydantic import BaseModel, Field
from typing import Optional

class ProviderInfo(BaseModel):
    id: str
    type: str  # e.g., "local", "cloud"

class HardwareRequirements(BaseModel):
    vram_required_gb: Optional[float] = None
    ram_required_gb: Optional[float] = None

class Capabilities(BaseModel):
    coding: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: float = Field(default=0.0, ge=0.0, le=1.0)
    tool_calling: float = Field(default=0.0, ge=0.0, le=1.0)
    vision: float = Field(default=0.0, ge=0.0, le=1.0)

class Context(BaseModel):
    window: int

class Economics(BaseModel):
    cost_per_1m_input: float = 0.0
    cost_per_1m_output: float = 0.0

class Limits(BaseModel):
    tpm: Optional[int] = None

class Evidence(BaseModel):
    source: str
    tested: bool
    test_suite: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class ModelProfile(BaseModel):
    id: str
    provider: ProviderInfo
    hardware: HardwareRequirements
    capabilities: Capabilities
    context: Context
    economics: Economics
    limits: Limits
    evidence: Evidence
