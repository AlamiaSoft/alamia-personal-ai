from pydantic import BaseModel
from typing import Dict, Any, List
from .hardware_scanner import HardwareScanner
from .os_scanner import OSScanner
from .model_scanner import ModelScanner
from ..domain.schemas.hardware import HardwareProfile
from ..domain.schemas.model import ModelProfile
from ..domain.errors import DiscoveryError

class HostInventory(BaseModel):
    hardware: HardwareProfile
    os_environment: Dict[str, Any]
    models: List[ModelProfile]

class InventoryBuilder:
    def __init__(self):
        self.hardware_scanner = HardwareScanner()
        self.os_scanner = OSScanner()
        self.model_scanner = ModelScanner()

    def build(self) -> HostInventory:
        try:
            hw_profile = self.hardware_scanner.scan()
            os_env = self.os_scanner.scan()
            models = self.model_scanner.scan_all()
            
            return HostInventory(
                hardware=hw_profile,
                os_environment=os_env,
                models=models
            )
        except Exception as e:
            raise DiscoveryError(f"Failed to build host inventory: {str(e)}")
