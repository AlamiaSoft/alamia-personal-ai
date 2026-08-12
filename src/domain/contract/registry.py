from typing import Dict, Type
from .runtime_adapter import RuntimeAdapter

class RuntimeRegistry:
    _adapters: Dict[str, Type[RuntimeAdapter]] = {}

    @classmethod
    def register(cls, runtime_id: str, adapter_class: Type[RuntimeAdapter]):
        cls._adapters[runtime_id] = adapter_class

    @classmethod
    def get_adapter(cls, runtime_id: str) -> Type[RuntimeAdapter]:
        if runtime_id not in cls._adapters and runtime_id == "agent_zero":
            from ...adapters.agent_zero.adapter import AgentZeroAdapter
            cls.register("agent_zero", AgentZeroAdapter)
        return cls._adapters.get(runtime_id)
        
    @classmethod
    def get_all(cls) -> Dict[str, Type[RuntimeAdapter]]:
        if "agent_zero" not in cls._adapters:
            from ...adapters.agent_zero.adapter import AgentZeroAdapter
            cls.register("agent_zero", AgentZeroAdapter)
        return cls._adapters
