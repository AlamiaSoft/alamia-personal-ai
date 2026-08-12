from typing import List, Optional

class AgentHostError(Exception):
    """Base class for all AgentHost errors with structured remediation support."""
    def __init__(
        self, 
        message: str, 
        error_type: Optional[str] = None,
        action: Optional[str] = None, 
        alternatives: Optional[List[str]] = None, 
        reasons: Optional[List[str]] = None,
        is_fatal: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type or type(self).__name__
        self.action = action
        self.alternatives = alternatives or []
        self.reasons = reasons or []
        self.is_fatal = is_fatal

class DiscoveryError(AgentHostError):
    """Host hardware/environment discovery failed."""
    pass

class ConfigurationError(AgentHostError):
    """Invalid execution profile or adapter configuration."""
    pass

class PreflightFailedError(AgentHostError):
    """Preflight validation failed (contains explicit reasons)."""
    def __init__(self, message: str, reasons: List[str]):
        super().__init__(message, reasons=reasons)

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
