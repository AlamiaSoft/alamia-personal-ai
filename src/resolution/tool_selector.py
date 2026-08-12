from typing import List
from ..domain.schemas.tool import ToolProfile
from ..domain.schemas.task import TaskRequirements

class ToolSelector:
    def __init__(self, available_tools: List[ToolProfile]):
        self.available_tools = available_tools

    def inject_subset(self, requirements: TaskRequirements) -> List[ToolProfile]:
        """Filters the available tools down to the minimal subset matching the task requirements."""
        subset = []
        for tool in self.available_tools:
            required = False
            for req_cap in tool.capability_requirements:
                if req_cap == "browser" and requirements.browser:
                    required = True
                elif req_cap == "filesystem" and requirements.filesystem:
                    required = True
                elif req_cap == "code_execution" and requirements.code_execution:
                    required = True
                elif req_cap == "vision" and requirements.vision:
                    required = True
                # If a tool has no capability requirements mapped or is core, include it
                elif req_cap == "core":
                    required = True
            
            if required:
                subset.append(tool)
                
        return subset
