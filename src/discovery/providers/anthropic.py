import os
import urllib.request
import json
from typing import List
from .base import BaseProviderAdapter
from ...domain.schemas.model import (
    ModelProfile, ProviderInfo, HardwareRequirements,
    Capabilities, Context, Economics, Limits, Evidence
)

class AnthropicProviderAdapter(BaseProviderAdapter):
    def discover_models(self) -> List[ModelProfile]:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return []

        url = "https://api.anthropic.com/v1/models"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                }
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    models_data = data.get("data", [])
                    
                    profiles = []
                    for m in models_data:
                        m_id = m.get("id")
                        if not m_id:
                            continue
                        
                        profile = ModelProfile(
                            id=f"anthropic/{m_id}",
                            provider=ProviderInfo(id="anthropic", type="cloud"),
                            hardware=HardwareRequirements(vram_required_gb=0.0, ram_required_gb=0.0, is_estimated=False),
                            capabilities=Capabilities(),
                            context=Context(window=200000),
                            economics=Economics(cost_per_1m_input=None, cost_per_1m_output=None),
                            limits=Limits(tpm=None),
                            evidence=Evidence(source="provider_metadata", tested=False, confidence=0.0)
                        )
                        profiles.append(profile)
                    return profiles
        except Exception:
            pass

        return []
