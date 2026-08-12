import os
import shutil
import platform
import multiprocessing
from typing import Optional
from ..domain.schemas.hardware import HardwareProfile
from ..domain.errors import DiscoveryError

class HardwareScanner:
    def __init__(self):
        pass

    def get_cpu_cores(self) -> int:
        try:
            return multiprocessing.cpu_count()
        except NotImplementedError:
            return 2

    def get_system_ram_gb(self) -> float:
        try:
            # Using psutil if available, otherwise simple fallback for mock
            import psutil
            mem = psutil.virtual_memory()
            return round(mem.total / (1024 ** 3), 2)
        except ImportError:
            # Fallback mock value if psutil is not installed in the environment
            return 16.0

    def get_disk_space_gb(self) -> float:
        try:
            total, used, free = shutil.disk_usage("/")
            return round(free / (1024 ** 3), 2)
        except Exception:
            return 100.0

    def scan(self) -> HardwareProfile:
        try:
            cores = self.get_cpu_cores()
            ram = self.get_system_ram_gb()
            disk = self.get_disk_space_gb()
            
            # For this MVP/mock, we assume no GPU is available or mock an NVIDIA GPU
            gpu_model = "Mock NVIDIA GPU" 
            vram_gb = 8.0
            
            return HardwareProfile(
                cpu_cores=cores,
                ram_gb=ram,
                gpu_model=gpu_model,
                vram_gb=vram_gb,
                disk_space_gb=disk
            )
        except Exception as e:
            raise DiscoveryError(f"Failed to scan hardware: {str(e)}")
