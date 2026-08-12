from pydantic import BaseModel
from typing import Optional

class HardwareProfile(BaseModel):
    cpu_cores: int
    ram_gb: float
    gpu_model: Optional[str] = None
    vram_gb: Optional[float] = None
    disk_space_gb: float
