import os
import urllib.request
import json
from typing import List
from .base import BaseProviderAdapter
from ...domain.schemas.model import (
    ModelProfile, ProviderInfo, HardwareRequirements,
    Capabilities, Context, Economics, Limits, Evidence
)

class OpenRouterProviderAdapter(BaseProviderAdapter):
    def discover_models(self) -> List[ModelProfile]:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            return []

        url = "https://openrouter.ai/api/v1/models"
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    models_data = data.get("data", [])
                    
                    profiles = []
                    for m in models_data:
                        m_id = m.get("id")
                        if not m_id:
                            continue
                        
                        ctx_window = m.get("context_length")
                        pricing = m.get("pricing", {})
                        
                        # OpenRouter returns pricing per token string, convert to per 1M tokens
                        try:
                            cost_in = float(pricing.get("prompt", 0.0)) * 1e6
                            cost_out = float(pricing.get("completion", 0.0)) * 1e6
                        except (ValueError, TypeError):
                            cost_in = None
                            cost_out = None

                        profile = ModelProfile(
                            id=f"openrouter/{m_id}",
                            provider=ProviderInfo(id="openrouter", type="cloud"),
                            hardware=HardwareRequirements(vram_required_gb=0.0, ram_required_gb=0.0, is_estimated=False),
                            capabilities=Capabilities(),
                            context=Context(window=ctx_window),
                            economics=Economics(cost_per_1m_input=cost_in, cost_per_1m_output=cost_out),
                            limits=Limits(tpm=None),
                            evidence=Evidence(source="provider_metadata", tested=False, confidence=0.0)
                        )
                        profiles.append(profile)
                    return profiles
        except Exception:
            pass

        return []
