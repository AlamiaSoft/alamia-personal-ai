import os
import shutil
import platform
import multiprocessing
import subprocess
import ctypes
from typing import Optional, Tuple
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
        # Try psutil first
        try:
            import psutil
            mem = psutil.virtual_memory()
            return round(mem.total / (1024 ** 3), 2)
        except ImportError:
            pass

        # Windows ctypes fallback
        if platform.system() == "Windows":
            try:
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                    return round(stat.ullTotalPhys / (1024 ** 3), 2)
            except Exception:
                pass

        # Linux /proc/meminfo fallback
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            parts = line.split()
                            kb = int(parts[1])
                            return round(kb / (1024 ** 2), 2)
            except Exception:
                pass

        return 8.0  # Conservative baseline if detection unverified

    def get_disk_space_gb(self) -> float:
        try:
            path = "C:\\" if platform.system() == "Windows" else "/"
            total, used, free = shutil.disk_usage(path)
            return round(free / (1024 ** 3), 2)
        except Exception:
            return 50.0

    def detect_gpu(self) -> Tuple[Optional[str], Optional[float]]:
        """Detect GPU model and VRAM using nvidia-smi or Windows WMI."""
        # 1. Check nvidia-smi
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3
            )
            if res.returncode == 0 and res.stdout.strip():
                line = res.stdout.strip().split("\n")[0]
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2:
                    gpu_name = parts[0]
                    vram_mb = float(parts[1])
                    return gpu_name, round(vram_mb / 1024.0, 2)
        except Exception:
            pass

        # 2. Check Windows WMI if on Windows
        if platform.system() == "Windows":
            try:
                res = subprocess.run(
                    ["wmic", "path", "win32_videocard", "get", "name,adapterram"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=3
                )
                if res.returncode == 0:
                    lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip()]
                    if len(lines) > 1:
                        # Skip header
                        data_line = lines[1]
                        parts = data_line.split()
                        gpu_name = " ".join(parts[:-1]) if len(parts) > 1 else "Generic GPU"
                        try:
                            bytes_vram = int(parts[-1])
                            vram_gb = round(bytes_vram / (1024 ** 3), 2) if bytes_vram > 0 else 0.0
                        except ValueError:
                            vram_gb = 0.0
                        return gpu_name, vram_gb
            except Exception:
                pass

        return None, None

    def scan(self) -> HardwareProfile:
        try:
            cores = self.get_cpu_cores()
            ram = self.get_system_ram_gb()
            disk = self.get_disk_space_gb()
            gpu_model, vram_gb = self.detect_gpu()
            
            return HardwareProfile(
                cpu_cores=cores,
                ram_gb=ram,
                gpu_model=gpu_model,
                vram_gb=vram_gb,
                disk_space_gb=disk
            )
        except Exception as e:
            raise DiscoveryError(f"Failed to scan hardware: {str(e)}")
