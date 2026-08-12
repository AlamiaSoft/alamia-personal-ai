from pydantic import BaseModel

class TaskRequirements(BaseModel):
    browser: bool = False
    filesystem: bool = False
    code_execution: bool = False
    long_context: bool = False
    vision: bool = False
    autonomy: bool = False
    cloud_allowed: bool = True
    privacy_constraint: bool = False
    cost_constraint: bool = False
