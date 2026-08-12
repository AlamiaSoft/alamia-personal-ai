from ..domain.schemas.task import TaskRequirements

class TaskAnalyzer:
    def __init__(self):
        pass
        
    def analyze(self, task_description: str) -> TaskRequirements:
        """
        Deterministic MVP rule-based classifier.
        In a real implementation, this would use a more robust
        classification engine or deterministic heuristics.
        """
        task = task_description.lower()
        
        req = TaskRequirements()
        
        if "web" in task or "search" in task or "browser" in task or "http" in task:
            req.browser = True
            
        if "file" in task or "save" in task or "read" in task or "write" in task or "folder" in task:
            req.filesystem = True
            
        if "code" in task or "script" in task or "python" in task or "run" in task:
            req.code_execution = True
            
        if "image" in task or "picture" in task or "look at" in task:
            req.vision = True
            
        if "local" in task or "private" in task or "secret" in task:
            req.cloud_allowed = False
            req.privacy_constraint = True
            
        if "cheap" in task or "free" in task:
            req.cost_constraint = True
            
        return req
