import urllib.request
import json
from typing import List, Dict, Any, Optional
from .base import BaseProviderAdapter
from ...domain.schemas.model import (
    ModelProfile, ProviderInfo, HardwareRequirements,
    Capabilities, Context, Economics, Limits, Evidence
)

class OllamaProviderAdapter(BaseProviderAdapter):
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host

    @property
    def provider_id(self) -> str:
        return "ollama"

    def _get_tags(self) -> List[Dict[str, Any]]:
        url = f"{self.host}/api/tags"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data.get("models", [])
        except Exception:
            pass
        return []

    def _get_show_metadata(self, model_name: str) -> Dict[str, Any]:
        url = f"{self.host}/api/show"
        try:
            payload = json.dumps({"name": model_name}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode('utf-8'))
        except Exception:
            pass
        return {}

    def discover_models(self) -> List[ModelProfile]:
        profiles = []
        tags = self._get_tags()

        for item in tags:
            name = item.get("name", "unknown")
            # Skip non-generative embedding models
            if "bge" in name.lower() or "embed" in name.lower():
                continue
                
            size_bytes = item.get("size", 0)
            digest = item.get("digest", "")
            
            show_data = self._get_show_metadata(name)
            model_info = show_data.get("model_info", {})
            details = show_data.get("details", item.get("details", {}))
            
            # Derive memory estimates directly from artifact size bytes
            if size_bytes > 0:
                vram_gb = round((size_bytes * 1.25) / (1024 ** 3), 2)
                ram_gb = round((size_bytes * 1.50) / (1024 ** 3), 2)
            else:
                vram_gb = None
                ram_gb = None

            # Context window extraction from GGUF metadata
            ctx_window = None
            for key, val in model_info.items():
                if "context_length" in key and isinstance(val, int):
                    ctx_window = val
                    break

            profile = ModelProfile(
                id=f"ollama/{name}",
                digest=digest,
                provider=ProviderInfo(id="ollama", type="local"),
                hardware=HardwareRequirements(
                    vram_required_gb=vram_gb,
                    ram_required_gb=ram_gb,
                    is_estimated=True
                ),
                capabilities=Capabilities(), # Default 0.0 unverified
                context=Context(window=ctx_window),
                economics=Economics(cost_per_1m_input=0.0, cost_per_1m_output=0.0),
                limits=Limits(tpm=None),
                evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
            )
            profiles.append(profile)

        return profiles
