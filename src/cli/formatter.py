from typing import List, Optional
from ..domain.errors import AgentHostError

class ErrorFormatter:
    @staticmethod
    def format_error(error: Exception) -> str:
        """Formats exceptions into clean, user-friendly terminal output."""
        lines = []
        err_type = type(error).__name__
        
        if isinstance(error, AgentHostError):
            lines.append(f"\n[AgentHost Error - {err_type}]")
            lines.append(f"Root Cause: {error.message}")
            
            if error.reasons:
                lines.append("Details:")
                for r in error.reasons:
                    lines.append(f"  - {r}")
                    
            if error.alternatives:
                lines.append("Available Alternatives:")
                for idx, alt in enumerate(error.alternatives, 1):
                    lines.append(f"  {idx}. {alt}")
                    
            if error.action:
                lines.append(f"Recommended Action: {error.action}")
        else:
            lines.append(f"\n[Unexpected Error - {err_type}]")
            lines.append(f"Details: {str(error)}")
            
        return "\n".join(lines) + "\n"

    @staticmethod
    def print_friendly_error(reason: str, alternatives: List[str], recommended: Optional[str] = None):
        """Formats errors as requested in feedback-04-product-validation-DAG.md."""
        err = AgentHostError(reason, action=recommended, alternatives=alternatives)
        print(ErrorFormatter.format_error(err))
