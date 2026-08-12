import os
from typing import Optional, Dict

def load_agenthost_config() -> Dict[str, str]:
    """Loads AgentHost configuration exclusively from .env file."""
    config = {}
    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        config[k.strip()] = v.strip()
        except Exception:
            pass
    return config

def get_config_key(key_name: str) -> Optional[str]:
    """Returns configured key from AgentHost .env configuration."""
    cfg = load_agenthost_config()
    return cfg.get(key_name)
