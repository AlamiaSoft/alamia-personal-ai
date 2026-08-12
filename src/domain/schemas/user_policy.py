from pydantic import BaseModel
from enum import Enum

class PrivacyLevel(str, Enum):
    LOCAL_ONLY = "local_only"
    PREFERRED_LOCAL = "preferred_local"
    NONE = "none"

class UserPolicy(BaseModel):
    local_preferred: bool = True
    max_monthly_cost: float = 10.0
    privacy: PrivacyLevel = PrivacyLevel.PREFERRED_LOCAL
