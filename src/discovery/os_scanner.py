import platform
import subprocess
import shutil
from typing import Dict, Any
from ..domain.errors import DiscoveryError

class OSScanner:
    def __init__(self):
        pass

    def check_docker_daemon(self) -> bool:
        """Check if Docker is installed and daemon is running."""
        docker_path = shutil.which("docker")
        if not docker_path:
            return False
            
        try:
            # Check if docker info runs successfully
            result = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def scan(self) -> Dict[str, Any]:
        """Scans the OS environment and returns a dictionary of findings."""
        try:
            return {
                "os_name": platform.system(),
                "os_release": platform.release(),
                "os_version": platform.version(),
                "machine": platform.machine(),
                "docker_running": self.check_docker_daemon(),
                "python_version": platform.python_version()
            }
        except Exception as e:
            raise DiscoveryError(f"Failed to scan OS environment: {str(e)}")
