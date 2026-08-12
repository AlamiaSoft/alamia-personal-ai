from typing import List, Tuple, Dict, Any, Optional
from ..domain.schemas.execution import ExecutionProfile
from ..domain.schemas.hardware import HardwareProfile
from ..domain.schemas.model import ModelProfile
from ..domain.schemas.task import TaskRequirements
from ..domain.schemas.tool import ToolProfile
from ..domain.schemas.user_policy import UserPolicy, PrivacyLevel
from ..domain.scoring import calculate_effective_capability
from ..domain.contract.registry import RuntimeRegistry
from ..discovery.inventory import HostInventory

class ExecutionProfileResolver:
    def __init__(self):
        pass

    def _score_model(self, model: ModelProfile, requirements: TaskRequirements, policy: UserPolicy, inventory: Optional[HostInventory] = None) -> float:
        score = 0.0
        
        # Tier 1: Empirically verified capability evidence (Confidence > 0.40)
        if model.evidence.confidence > 0.40:
            if requirements.code_execution:
                score += calculate_effective_capability(model.capabilities.coding, model.evidence.confidence) * 2.0
            if requirements.browser:
                score += calculate_effective_capability(model.capabilities.tool_calling, model.evidence.confidence) * 1.5
            score += calculate_effective_capability(model.capabilities.reasoning, model.evidence.confidence)
        else:
            # Tier 2: Objective Structural / Runtime Fit when empirical evidence is UNKNOWN (Confidence <= 0.40)
            # NO Model ID Name Heuristics! Driven strictly by discovered metadata facts & derived estimates.
            
            # A. Context Window Fit (discovers context capacity for agent reasoning)
            if model.context.window:
                score += min(0.30, (model.context.window / 128000.0) * 0.30)
                
            # B. Hardware Capacity & Estimated VRAM Fit (discovers artifact byte size & parameter capacity)
            if model.provider.type == "local" and model.hardware.vram_required_gb and inventory and inventory.hardware.vram_gb:
                vram_ratio = min(1.0, model.hardware.vram_required_gb / inventory.hardware.vram_gb)
                score += vram_ratio * 0.30
        
        # Cost penalty and policy logic
        if model.provider.type == "cloud":
            cost = model.economics.cost_per_1m_input or 0.0
            if requirements.cost_constraint:
                score -= 1.0 # Heavy penalty for cloud if cheap requested
            elif cost > policy.max_monthly_cost:
                score -= 1.0 # Penalty for exceeding cost policy
        
        # Preference bonus (only granted if capability evidence is verified)
        if policy.local_preferred and model.provider.type == "local" and model.evidence.confidence > 0.40:
            score += 0.5
            
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

        # Resolve runtime adapter from registry
        runtime_id = "agent_zero"
        adapter_cls = RuntimeRegistry.get_adapter(runtime_id)
        if not adapter_cls:
            explainability[runtime_id] = f"Excluded: Runtime adapter '{runtime_id}' not registered."
            return candidates, explainability

        runtime_adapter = adapter_cls()
        runtime_caps = runtime_adapter.capabilities()

        if not inventory.os_environment.get("docker_running", False):
            explainability[runtime_id] = "Excluded: Docker not running."
            return candidates, explainability

        # Evaluate capability fulfillment across execution profile
        has_browser = runtime_caps.provides_browser or any(getattr(t, 'provides_browser', False) for t in tools_subset)

        for model in inventory.models:
            reasoning = []

            # Browser requirement check
            if requirements.browser and not has_browser:
                # If neither runtime nor tools provide browser, model MUST have native tool calling
                if model.capabilities.tool_calling < 0.2:
                    explainability[model.id] = f"Excluded: Browser capability required, but neither runtime '{runtime_id}', tools, nor model satisfy it."
                    continue

            # Native tool calling requirement check (if runtime strictly requires model native tool-calling)
            if runtime_caps.requires_native_tool_calling:
                if model.capabilities.tool_calling < 0.2 or model.evidence.confidence <= 0.40:
                    explainability[model.id] = f"Excluded: Runtime '{runtime_id}' requires verified native model tool-calling (Model confidence: {model.evidence.confidence:.2f})."
                    continue
            
            # Check privacy constraint from task or policy
            if model.provider.type == "cloud":
                if requirements.privacy_constraint or policy.privacy == PrivacyLevel.LOCAL_ONLY:
                    explainability[model.id] = "Excluded: Privacy constraint mandates local model."
                    continue
                if not requirements.cloud_allowed:
                    explainability[model.id] = "Excluded: Cloud not allowed by task."
                    continue

            # Provider constraint check (Execution Viability vs Model Capability)
            if model.limits.tpm is not None and model.limits.tpm < 11300:
                explainability[model.id] = f"Excluded: Provider TPM limit ({model.limits.tpm}) is insufficient for Agent Zero context requirements (~11.3k tokens/req). Execution profile NOT VIABLE."
                continue

            # Check hardware fit (VRAM)
            if model.provider.type == "local" and model.hardware.vram_required_gb:
                vram_avail = inventory.hardware.vram_gb or 0.0
                if vram_avail < model.hardware.vram_required_gb:
                    explainability[model.id] = f"Excluded: VRAM required ({model.hardware.vram_required_gb}GB) > available ({vram_avail}GB)."
                    continue
            
            score = self._score_model(model, requirements, policy, inventory)
            mode = model.provider.type
            
            eff_cap = calculate_effective_capability(
                model.capabilities.tool_calling if requirements.browser else model.capabilities.coding,
                model.evidence.confidence
            )
            
            profile = ExecutionProfile(
                runtime_id=runtime_id,
                model=model,
                hardware_constraints=inventory.hardware,
                tools=tools_subset,
                mode=mode,
                privacy_posture="local-only" if mode == "local" else "cloud-hybrid",
                reliability_score=eff_cap
            )
            
            candidates.append((score, profile))

            # Build explicit capability provenance trace
            gpu_str = inventory.hardware.gpu_model if inventory.hardware.gpu_model else "CPU"
            mem_str = f"{inventory.hardware.vram_gb:.1f} GB VRAM" if inventory.hardware.vram_gb else f"{inventory.hardware.ram_gb:.1f} GB RAM"

            reasoning.append(f"Score: {score:.2f}")
            if requirements.browser:
                browser_src = f"{runtime_id} runtime" if runtime_caps.provides_browser else "Model"
                reasoning.append(f"Browser -> {browser_src}")
            if requirements.code_execution:
                code_src = f"{runtime_id} runtime" if runtime_caps.provides_code_execution else "Model"
                reasoning.append(f"Code execution -> {code_src}")
            if requirements.filesystem:
                fs_src = f"{runtime_id} runtime" if runtime_caps.provides_filesystem else "Model"
                reasoning.append(f"Filesystem -> {fs_src}")

            reasoning.append(f"Coding -> {model.id}")
            reasoning.append(f"Hardware -> {gpu_str} ({mem_str} available)")

            if model.evidence.confidence <= 0.40:
                reasoning.append(f"[WARN] Best structural candidate - capability unverified (Confidence: {model.evidence.confidence:.2f})")
                
            explainability[model.id] = reasoning

        # Sort descending deterministically by score, then context window, then VRAM required
        # Guarantees list ordering in inventory cannot determine the winner
        candidates.sort(
            key=lambda x: (
                round(x[0], 4), 
                x[1].model.context.window or 0, 
                x[1].model.hardware.vram_required_gb or 0.0
            ), 
            reverse=True
        )
        ranked_profiles = [p for _, p in candidates]
        
        return ranked_profiles, explainability
