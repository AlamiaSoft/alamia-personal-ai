from typing import List, Optional
from pydantic import BaseModel
from ..domain.schemas.execution import ExecutionProfile
from ..domain.schemas.task import TaskRequirements
from ..domain.errors import PreflightFailedError

class PreflightResult(BaseModel):
    passed: bool
    reasons: List[str]

class PreflightEngine:
    def __init__(self):
        pass

    def run_profile_preflight(self, profile: ExecutionProfile) -> PreflightResult:
        """Heavy validation on profile selection/change."""
        reasons = []
        
        # Check VRAM
        if profile.mode == "local":
            vram_req = profile.model.hardware.vram_required_gb or 0.0
            vram_avail = profile.hardware_constraints.vram_gb or 0.0
            if vram_req > vram_avail:
                reasons.append(f"Insufficient VRAM: required {vram_req}GB, available {vram_avail}GB.")
                
        # In MVP, assume Agent Zero is installed/available
        
        passed = len(reasons) == 0
        return PreflightResult(passed=passed, reasons=reasons)

    def run_task_preflight(self, profile: ExecutionProfile, requirements: TaskRequirements) -> PreflightResult:
        """Lightweight validation per request."""
        reasons = []
        
        # Check quota/limits (mock)
        if profile.model.limits.tpm is not None and profile.model.limits.tpm < 1000:
            reasons.append("Token rate limit exceeded.")
            
        # Check capability mismatch that shouldn't happen if resolver did its job,
        # but serves as a final safety boundary.
        if requirements.browser and profile.model.capabilities.tool_calling < 0.2:
            reasons.append("Selected model cannot perform reliable browser tasks.")
            
        passed = len(reasons) == 0
        if not passed:
            raise PreflightFailedError("Task preflight failed", reasons)
            
        return PreflightResult(passed=passed, reasons=reasons)
