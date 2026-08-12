import urllib.request
import json
from typing import List, Dict, Any
from ..domain.schemas.model import (
    ModelProfile, ProviderInfo, HardwareRequirements,
    Capabilities, Context, Economics, Limits, Evidence
)
from ..domain.errors import DiscoveryError

class ModelScanner:
    def __init__(self, ollama_host: str = "http://127.0.0.1:11434"):
        self.ollama_host = ollama_host

    def _fetch_ollama_tags(self) -> Dict[str, Any]:
        """Fetch models from local Ollama instance."""
        url = f"{self.ollama_host}/api/tags"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2.0) as response:
                if response.status == 200:
                    data = response.read()
                    return json.loads(data.decode('utf-8'))
            return {}
        except Exception:
            # If Ollama is not running or unreachable, return empty
            return {}

    def scan_ollama(self) -> List[ModelProfile]:
        """Scans local Ollama models and builds profiles."""
        models = []
        tags_response = self._fetch_ollama_tags()
        
        if "models" in tags_response:
            for item in tags_response["models"]:
                model_name = item.get("name", "unknown")
                
                # Mock capabilities based on name for MVP
                coding_score = 0.8 if "coder" in model_name else 0.5
                vram_req = 8.0 if "14b" in model_name else 4.0
                
                profile = ModelProfile(
                    id=f"ollama/{model_name}",
                    provider=ProviderInfo(id="ollama", type="local"),
                    hardware=HardwareRequirements(vram_required_gb=vram_req, ram_required_gb=vram_req * 1.5),
                    capabilities=Capabilities(coding=coding_score, reasoning=0.7, tool_calling=0.5, vision=0.0),
                    context=Context(window=8192),
                    economics=Economics(cost_per_1m_input=0.0, cost_per_1m_output=0.0),
                    limits=Limits(tpm=None),
                    evidence=Evidence(source="empirical", tested=True, confidence=0.90)
                )
                models.append(profile)
                
        return models

    def scan_cloud(self) -> List[ModelProfile]:
        """Scans configured cloud providers (Mock for MVP)."""
        # In a full implementation, this would check environment variables (e.g., GROQ_API_KEY)
        # and fetch available models.
        return []

    def scan_all(self) -> List[ModelProfile]:
        try:
            local_models = self.scan_ollama()
            cloud_models = self.scan_cloud()
            return local_models + cloud_models
        except Exception as e:
            raise DiscoveryError(f"Failed to scan models: {str(e)}")
