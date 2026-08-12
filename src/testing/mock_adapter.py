from typing import Any
from ..domain.contract.runtime_adapter import (
    RuntimeAdapter, RuntimeInfo, InstallResult, RuntimeConfig,
    HealthStatus, CapabilitySet, ModelList, ExecuteRequest,
    ExecuteResult, EventStream, Journal, Diagnostics
)
from ..domain.schemas.model import ModelProfile

class MockAdapter(RuntimeAdapter):
    def __init__(self):
        self.is_running = False
        self.config = None

    def discover(self) -> RuntimeInfo:
        return RuntimeInfo(version="mock-1.0", is_installed=True, status="ready")

    def install(self) -> InstallResult:
        return InstallResult(success=True, logs="Mock installation successful")

    def configure(self, cfg: RuntimeConfig) -> None:
        self.config = cfg

    def start(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False

    def restart(self) -> None:
        self.stop()
        self.start()

    def health(self) -> HealthStatus:
        if self.is_running:
            return HealthStatus(is_healthy=True, message="Mock runtime is healthy")
        return HealthStatus(is_healthy=False, message="Mock runtime is stopped")

    def capabilities(self) -> CapabilitySet:
        return CapabilitySet(supported_features=["execute", "stream", "logs"])

    def models(self) -> ModelList:
        return ModelList(models=[])

    def execute(self, req: ExecuteRequest) -> ExecuteResult:
        if not self.is_running:
            raise RuntimeError("Mock runtime is not running")
        return ExecuteResult(success=True, response=f"Echo: {req.message}")

    def stream(self, req: ExecuteRequest) -> EventStream:
        return EventStream()

    def cancel(self, ctx_id: str) -> None:
        pass

    def logs(self, ctx_id: str) -> Journal:
        return Journal(logs=[f"Log for context {ctx_id}"])

    def diagnostics(self) -> Diagnostics:
        return Diagnostics(metrics={"cpu_usage": 0.1})
