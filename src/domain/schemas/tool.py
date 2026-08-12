from pydantic import BaseModel
from typing import List

class ToolProfile(BaseModel):
    id: str
    capability_requirements: List[str]
    prompt_footprint_tokens: int
