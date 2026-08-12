from typing import List, Tuple, Dict, Any, Optional
from ..domain.schemas.execution import ExecutionProfile
from ..domain.schemas.hardware import HardwareProfile
from ..domain.schemas.model import ModelProfile
from ..domain.schemas.task import TaskRequirements
from ..domain.schemas.tool import ToolProfile
from ..domain.schemas.user_policy import UserPolicy, PrivacyLevel
from ..domain.scoring import calculate_effective_capability
from ..discovery.inventory import HostInventory

class ExecutionProfileResolver:
    def __init__(self):
        pass

    def _score_model(self, model: ModelProfile, requirements: TaskRequirements, policy: UserPolicy) -> float:
        score = 0.0
        
        # Capability fit
        if requirements.code_execution:
            score += calculate_effective_capability(model.capabilities.coding, model.evidence.confidence) * 2
        if requirements.browser:
            score += calculate_effective_capability(model.capabilities.tool_calling, model.evidence.confidence) * 1.5
            
        score += calculate_effective_capability(model.capabilities.reasoning, model.evidence.confidence)
        
        # Cost penalty and policy logic
        if model.provider.type == "cloud":
            cost = model.economics.cost_per_1m_input or 0.0
            if requirements.cost_constraint:
                score -= 1.0 # Heavy penalty for cloud if cheap requested
            elif cost > policy.max_monthly_cost:
                score -= 1.0 # Penalty for exceeding cost policy
        
        # Preference bonus (not absolute exclusion)
        if policy.local_preferred and model.provider.type == "local":
            score += 0.5 # Give local models a strong edge, but allow cloud to win if capability disparity is massive
            
        return score

    def resolve(
        self, 
        inventory: HostInventory, 
        requirements: TaskRequirements, 
        tools_subset: List[ToolProfile],
        policy: Optional[UserPolicy] = None
    ) -> Tuple[List[ExecutionProfile], Dict[str, Any]]:
        """
        Composite resolver scoring runtime/model/hardware fit based on UserPolicy.
        Outputs ranked ExecutionProfiles and explainability reasons.
        """
        if policy is None:
            policy = UserPolicy()
            
        candidates = []
        explainability = {}

        # For MVP, assume Agent Zero is the only runtime
        runtime_id = "agent_zero"
        if not inventory.os_environment.get("docker_running", False):
            explainability[runtime_id] = "Excluded: Docker not running."
            return candidates, explainability

        for model in inventory.models:
            reasoning = []
            
            # Capability failure check
            if requirements.browser and model.capabilities.tool_calling < 0.2:
                # E.g. local model lacks tool calling
                explainability[model.id] = f"Excluded: Model cannot satisfy multi-tool requirement."
                continue
            
            # Check privacy constraint from task or policy
            if model.provider.type == "cloud":
                if requirements.privacy_constraint or policy.privacy == PrivacyLevel.LOCAL_ONLY:
                    explainability[model.id] = "Excluded: Privacy constraint mandates local model."
                    continue
                if not requirements.cloud_allowed:
                    explainability[model.id] = "Excluded: Cloud not allowed by task."
                    continue

            # Check hardware fit (VRAM)
            if model.provider.type == "local" and model.hardware.vram_required_gb:
                vram_avail = inventory.hardware.vram_gb or 0.0
                if vram_avail < model.hardware.vram_required_gb:
                    explainability[model.id] = f"Excluded: VRAM required ({model.hardware.vram_required_gb}GB) > available ({vram_avail}GB)."
                    continue
            
            score = self._score_model(model, requirements, policy)
            mode = model.provider.type
            
            profile = ExecutionProfile(
                runtime_id=runtime_id,
                model=model,
                hardware_constraints=inventory.hardware,
                tools=tools_subset,
                mode=mode,
                privacy_posture="local-only" if mode == "local" else "cloud-hybrid",
                reliability_score=model.evidence.confidence
            )
            
            candidates.append((score, profile))
            if model.evidence.confidence <= 0.40:
                reasoning.append(f"[WARN] Capability not verified (Confidence: {model.evidence.confidence:.2f})")
            else:
                reasoning.append(f"Score: {score:.2f}")
                reasoning.append(f"Hardware fit: PASS")
                reasoning.append(f"Capabilities fit: PASS")
                
                # Policy explanations
                if mode == "local" and policy.local_preferred:
                    reasoning.append("Local model is sufficient -> use local.")
                elif mode == "cloud" and policy.local_preferred:
                    reasoning.append("Local model could not satisfy requirements -> cloud fallback required.")
                
            explainability[model.id] = reasoning

        # Sort descending by score
        candidates.sort(key=lambda x: x[0], reverse=True)
        ranked_profiles = [p for _, p in candidates]
        
        return ranked_profiles, explainability
