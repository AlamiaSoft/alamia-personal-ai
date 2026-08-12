from typing import List, Optional

class ErrorFormatter:
    @staticmethod
    def print_friendly_error(reason: str, alternatives: List[str], recommended: Optional[str] = None):
        """
        Formats errors as requested in feedback-04-product-validation-DAG.md.
        Removes stack traces and provides actionable alternatives.
        """
        print("\nAgentHost cannot run this profile.\n")
        print("Reason:")
        print(f"{reason}\n")
        
        if alternatives:
            print("Available alternatives:")
            for idx, alt in enumerate(alternatives, 1):
                print(f"{idx}. {alt}")
            print()
            
        if recommended:
            print(f"Recommended:\n{recommended}\n")
            
        print("Run alternative? [Y/n]")
