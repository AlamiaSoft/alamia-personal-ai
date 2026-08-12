class AgentHostError(Exception):
    """Base class for all AgentHost errors."""
    pass

class DiscoveryError(AgentHostError):
    """Host hardware/environment discovery failed."""
    pass

class ConfigurationError(AgentHostError):
    """Invalid execution profile or adapter configuration."""
    pass

class PreflightFailedError(AgentHostError):
    """Preflight validation failed (contains explicit reasons)."""
    def __init__(self, message: str, reasons: list[str]):
        super().__init__(message)
        self.reasons = reasons

class RuntimeUnavailableError(AgentHostError):
    """Candidate runtime container/process unready or unresponsive."""
    pass

class ModelUnavailableError(AgentHostError):
    """Model not found or quota/VRAM exhausted."""
    pass

class CapabilityMismatchError(AgentHostError):
    """Task requirement exceeds available capability."""
    pass

class QuotaExceededError(AgentHostError):
    """Token or rate limit exceeded."""
    pass

class RuntimeError(AgentHostError):
    """Error returned from runtime execution (mapped)."""
    pass
