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
            # Check if container exists (stopped or running)
            check = subprocess.run(
                ["docker", "inspect", self.container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if check.returncode != 0:
                raise RuntimeUnavailableError(
                    f"Container '{self.container_name}' does not exist on this host.\n"
                    f"Please run the Agent Zero docker container using:\n"
                    f"  docker run -d -p 5000:5000 --name {self.container_name} agent-zero"
                )
                
            res = subprocess.run(["docker", "start", self.container_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if res.returncode != 0:
                raise RuntimeUnavailableError(f"Failed to start container '{self.container_name}': {res.stderr.strip()}")
        except RuntimeUnavailableError:
            raise
        except Exception as e:
            raise RuntimeUnavailableError(f"Unexpected error starting container '{self.container_name}': {e}")

    def stop(self) -> None:
        if not self.is_running():
            return
            
        try:
            subprocess.run(["docker", "stop", self.container_name], check=False, timeout=15)
        except Exception as e:
            pass

    def get_health(self) -> bool:
        return self.is_running()
