from pydantic import BaseModel
from typing import List
from .model import ModelProfile
from .hardware import HardwareProfile
from .tool import ToolProfile

class ExecutionProfile(BaseModel):
    runtime_id: str
    model: ModelProfile
    hardware_constraints: HardwareProfile
    tools: List[ToolProfile]
    mode: str  # e.g., "local", "cloud", "hybrid"
    cost_estimate: float = 0.0
    privacy_posture: str
    reliability_score: float
