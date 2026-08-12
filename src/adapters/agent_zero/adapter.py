from typing import List, Dict, Any
from ...domain.contract.runtime_adapter import (
    RuntimeAdapter, RuntimeInfo, InstallResult, RuntimeConfig,
    HealthStatus, CapabilitySet, ModelList, ExecuteRequest,
    ExecuteResult, EventStream, Journal, Diagnostics
)
from ...domain.schemas.model import ModelProfile
from .container import AgentZeroContainer
from .api_bridge import APIBridge
from .journal import JournalExtractor

class AgentZeroAdapter(RuntimeAdapter):
    """Production runtime adapter for Agent Zero."""
    
    def __init__(self):
        self.container = AgentZeroContainer()
        self.bridge = APIBridge()
        self.journal = JournalExtractor()

    def discover(self) -> RuntimeInfo:
        is_running = self.container.is_running()
        return RuntimeInfo(
            version="agent-zero-v1",
            is_installed=True,
            status="running" if is_running else "stopped"
        )

    def install(self) -> InstallResult:
        return InstallResult(success=True, logs="Agent Zero container ready")

    def configure(self, cfg: RuntimeConfig) -> None:
        pass

    def start(self) -> None:
        self.container.start()

    def stop(self) -> None:
        self.container.stop()

    def restart(self) -> None:
        self.stop()
        self.start()

    def health(self) -> HealthStatus:
        if self.container.is_running():
            return HealthStatus(is_healthy=True, message="Agent Zero container is running")
        return HealthStatus(is_healthy=False, message="Agent Zero container is not running")

    def capabilities(self) -> CapabilitySet:
        return CapabilitySet(
            supported_features=["execute", "browser", "code_execution", "filesystem"],
            provides_browser=True,
            provides_code_execution=True,
            provides_filesystem=True,
            requires_native_tool_calling=False
        )

    def models(self) -> ModelList:
        return ModelList(models=[])

    def execute(self, req: ExecuteRequest) -> ExecuteResult:
        return self.bridge.send_message(req)

    def stream(self, req: ExecuteRequest) -> EventStream:
        return EventStream()

    def cancel(self, ctx_id: str) -> None:
        pass

    def logs(self, ctx_id: str) -> Journal:
        return self.journal.extract(ctx_id)

    def diagnostics(self) -> Diagnostics:
        return Diagnostics(metrics={"container_running": self.container.is_running()})
