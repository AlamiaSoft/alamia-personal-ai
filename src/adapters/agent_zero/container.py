import subprocess
from typing import Optional
from ...domain.errors import RuntimeUnavailableError

class AgentZeroContainer:
    def __init__(self, container_name: str = "agent-zero-v2.8"):
        self.container_name = container_name

    def is_running(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", self.container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            return result.stdout.strip() == "true"
        except Exception:
            return False

    def start(self) -> None:
        if self.is_running():
            return
            
        try:
            # MVP: Just try to start an existing container or assume it's mock
            subprocess.run(["docker", "start", self.container_name], check=False, timeout=10)
        except Exception as e:
            raise RuntimeUnavailableError(f"Failed to start container: {e}")

    def stop(self) -> None:
        if not self.is_running():
            return
            
        try:
            subprocess.run(["docker", "stop", self.container_name], check=False, timeout=15)
        except Exception as e:
            pass

    def get_health(self) -> bool:
        return self.is_running()
