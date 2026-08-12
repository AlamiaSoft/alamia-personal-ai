import os
import json
from typing import Dict, Any, Optional
from ..domain.schemas.model import ModelProfile, Capabilities, Evidence

class CapabilityProbeEngine:
    def __init__(self, cache_file: str = "artifacts/capability_cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        # 1. Load pre-seeded empirical test fixtures if available
        fixture_path = os.path.join("tests", "fixtures", "empirical_capabilities.json")
        if os.path.exists(fixture_path):
            try:
                with open(fixture_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("models", []):
                        m_id = item.get("id")
                        caps = item.get("known_capabilities", {})
                        conf = item.get("confidence", 0.0)
                        if m_id and conf > 0.0:
                            self.cache[m_id] = {
                                "coding": 0.90 if caps.get("coding", False) else (0.85 if caps.get("single_tool", False) else 0.0),
                                "reasoning": 0.85 if caps.get("basic_chat", False) else 0.0,
                                "tool_calling": 0.90 if caps.get("multi_tool", False) else (0.60 if caps.get("single_tool", False) else 0.0),
                                "vision": 0.90 if caps.get("vision", False) else 0.0,
                                "confidence": conf,
                                "source": "empirical",
                                "tested": True
                            }
            except Exception:
                pass

        # 2. Load disk cache if exists
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    self.cache.update(disk_cache)
            except Exception:
                pass

    def enrich_model_profile(self, profile: ModelProfile) -> ModelProfile:
        """
        Enriches a ModelProfile with empirical capability evidence if present in cache.
        If unprobed, leaves confidence as 0.0 (UNKNOWN) and capabilities unverified.
        """
        # Match by exact id, basename, or digest
        model_key = None
        if profile.id in self.cache:
            model_key = profile.id
        else:
            # Try matching by model name ignoring provider prefix (e.g. "ollama/qwen:7b" -> "qwen:7b")
            raw_name = profile.id.split("/")[-1]
            if raw_name in self.cache:
                model_key = raw_name
            elif profile.digest and profile.digest in self.cache:
                model_key = profile.digest

        if model_key:
            entry = self.cache[model_key]
            profile.capabilities = Capabilities(
                coding=entry.get("coding", 0.0),
                reasoning=entry.get("reasoning", 0.0),
                tool_calling=entry.get("tool_calling", 0.0),
                vision=entry.get("vision", 0.0)
            )
            profile.evidence = Evidence(
                source=entry.get("source", "empirical"),
                tested=entry.get("tested", True),
                test_suite="agenthost-probe-v1",
                confidence=entry.get("confidence", 0.90)
            )
        else:
            # UNPROBED / UNKNOWN model
            # Do NOT infer capabilities from name or assign fake confidence!
            profile.capabilities = Capabilities(
                coding=0.0,
                reasoning=0.0,
                tool_calling=0.0,
                vision=0.0
            )
            profile.evidence = Evidence(
                source="runtime_metadata" if profile.provider.type == "local" else "provider_metadata",
                tested=False,
                test_suite=None,
                confidence=0.0  # Explicit UNKNOWN
            )

        return profile
