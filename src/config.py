import os
from typing import Optional, Dict, List

def load_agenthost_config() -> Dict[str, str]:
    """Loads AgentHost configuration exclusively from .env file without mutating os.environ."""
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

def get_enabled_providers() -> List[str]:
    """Returns the list of explicitly enabled provider IDs in AgentHost configuration."""
    cfg = load_agenthost_config()
    
    # Check explicit list first
    if "AGENTHOST_ENABLED_PROVIDERS" in cfg:
        providers = [p.strip().lower() for p in cfg["AGENTHOST_ENABLED_PROVIDERS"].split(",") if p.strip()]
        return providers
        
    mode = cfg.get("AGENTHOST_MODE", "local").lower()
    if mode == "local":
        return ["ollama"]
    elif mode == "cloud_hybrid":
        # Enable providers that have keys in .env
        enabled = ["ollama"]
        if "GROQ_API_KEY" in cfg: enabled.append("groq")
        if "OPENAI_API_KEY" in cfg: enabled.append("openai")
        if "ANTHROPIC_API_KEY" in cfg: enabled.append("anthropic")
        if "OPENROUTER_API_KEY" in cfg: enabled.append("openrouter")
        return enabled
        
    return ["ollama"]

def is_provider_enabled(provider_id: str) -> bool:
    """
    Checks if a provider is explicitly enabled in AgentHost configuration.
    A credential's mere existence in os.environ will NEVER activate a provider.
    """
    enabled_list = get_enabled_providers()
    return provider_id.lower() in enabled_list

def get_credential(key_name: str, provider_id: str) -> Optional[str]:
    """
    Resolves credential precedence:
    AgentHost config (.env) -> OS environment (os.environ)
    ONLY IF provider_id is explicitly enabled in AgentHost configuration.
    """
    if not is_provider_enabled(provider_id):
        # A credential's mere existence in os.environ must NEVER activate a provider
        return None
        
    cfg = load_agenthost_config()
    if key_name in cfg:
        return cfg[key_name]
        
    # Precedence fallback to OS environment if provider is enabled
    return os.environ.get(key_name)

def get_config_key(key_name: str) -> Optional[str]:
    """Legacy helper fallback."""
    cfg = load_agenthost_config()
    return cfg.get(key_name)
