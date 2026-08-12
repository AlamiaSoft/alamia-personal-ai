import unittest
from unittest.mock import patch, MagicMock
import os
import json

from src.domain.schemas.model import (
    ModelProfile, ProviderInfo, HardwareRequirements,
    Capabilities, Context, Economics, Limits, Evidence
)
from src.discovery.providers.ollama import OllamaProviderAdapter
from src.discovery.providers.groq import GroqProviderAdapter
from src.discovery.providers.openai import OpenAIProviderAdapter
from src.capabilities.probe_engine import CapabilityProbeEngine
from src.resolution.resolver import ExecutionProfileResolver
from src.discovery.inventory import HostInventory, HardwareProfile
from src.domain.schemas.task import TaskRequirements
from src.domain.schemas.user_policy import UserPolicy

class TestModelEvidence(unittest.TestCase):

    def test_1_unknown_capability_not_converted_to_positive_score(self):
        """Prove that an unknown capability (confidence=0.0) yields near zero effective capability."""
        model = ModelProfile(
            id="unknown-model",
            provider=ProviderInfo(id="mock", type="local"),
            hardware=HardwareRequirements(vram_required_gb=4.0),
            capabilities=Capabilities(coding=1.0, reasoning=1.0, tool_calling=1.0),
            context=Context(window=8192),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="unknown", tested=False, confidence=0.0) # UNKNOWN
        )
        
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        policy = UserPolicy()
        
        score = resolver._score_model(model, reqs, policy)
        # Even though raw capability is 1.0, confidence=0.0 yields score heavily penalized by 0.1x
        self.assertLess(score, 0.50, f"Unknown capability scored too high: {score}")

    def test_2_ollama_metadata_discovery(self):
        """Prove an installed Ollama model is constructed from actual runtime metadata (/api/show)."""
        adapter = OllamaProviderAdapter(host="http://127.0.0.1:11434")
        
        mock_tags = [{
            "name": "qwen2.5-coder:7b",
            "size": 4700000000, # ~4.7 GB artifact
            "digest": "sha256:abc12345"
        }]
        mock_show = {
            "details": {"parameter_size": "7.6B", "quantization_level": "Q4_K_M"},
            "model_info": {"qwen2.context_length": 32768}
        }
        
        with patch.object(adapter, '_get_tags', return_value=mock_tags):
            with patch.object(adapter, '_get_show_metadata', return_value=mock_show):
                profiles = adapter.discover_models()
                self.assertEqual(len(profiles), 1)
                p = profiles[0]
                self.assertEqual(p.id, "ollama/qwen2.5-coder:7b")
                self.assertEqual(p.digest, "sha256:abc12345")
                self.assertEqual(p.context.window, 32768)
                self.assertTrue(p.hardware.is_estimated)
                self.assertAlmostEqual(p.hardware.vram_required_gb, 5.47, delta=0.5)
                self.assertEqual(p.evidence.source, "runtime_metadata")

    def test_3_api_key_alone_does_not_fabricate_models(self):
        """Prove that having an API key alone does NOT fabricate models if API call fails/returns empty."""
        adapter = GroqProviderAdapter()
        with patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}):
            # Mock HTTP error when querying /v1/models
            with patch("urllib.request.urlopen", side_effect=Exception("API connection failed")):
                models = adapter.discover_models()
                self.assertEqual(models, [], "API key alone must not fabricate models if API call fails")

    def test_4_empirical_vs_estimated_distinguishable(self):
        """Prove empirical and inferred/estimated capabilities and hardware are distinguishable."""
        engine = CapabilityProbeEngine()
        
        unprobed = ModelProfile(
            id="ollama/custom-model:latest",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=4.0, is_estimated=True),
            capabilities=Capabilities(),
            context=Context(window=None),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
        )
        
        enriched = engine.enrich_model_profile(unprobed)
        self.assertFalse(enriched.evidence.tested)
        self.assertEqual(enriched.evidence.confidence, 0.0)
        self.assertTrue(enriched.hardware.is_estimated)
        
        # Test known empirical model
        empirical_model = ModelProfile(
            id="qwen:7b",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=4.0, is_estimated=True),
            capabilities=Capabilities(),
            context=Context(window=8192),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="unknown", tested=False, confidence=0.0)
        )
        enriched_emp = engine.enrich_model_profile(empirical_model)
        self.assertTrue(enriched_emp.evidence.tested)
        self.assertEqual(enriched_emp.evidence.source, "empirical")
        self.assertGreater(enriched_emp.evidence.confidence, 0.80)

    def test_5_resolver_behavior_changes_with_confidence(self):
        """Prove resolver prefers high-confidence empirical evidence over low-confidence/unknown evidence."""
        hw = HardwareProfile(cpu_cores=8, ram_gb=32.0, gpu_model="NVIDIA", vram_gb=16.0, disk_space_gb=100.0)
        
        # Model A: High capability raw, but UNKNOWN confidence (0.0)
        model_a = ModelProfile(
            id="model-unverified",
            provider=ProviderInfo(id="local", type="local"),
            hardware=HardwareRequirements(vram_required_gb=4.0),
            capabilities=Capabilities(coding=0.95, reasoning=0.95, tool_calling=0.95),
            context=Context(window=8192),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="unknown", tested=False, confidence=0.0)
        )
        
        # Model B: Moderate capability raw, but High EMPIRICAL confidence (0.95)
        model_b = ModelProfile(
            id="model-empirical",
            provider=ProviderInfo(id="local", type="local"),
            hardware=HardwareRequirements(vram_required_gb=4.0),
            capabilities=Capabilities(coding=0.80, reasoning=0.80, tool_calling=0.80),
            context=Context(window=8192),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="empirical", tested=True, confidence=0.95)
        )
        
        inventory = HostInventory(hardware=hw, os_environment={"docker_running": True}, models=[model_a, model_b])
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        
        profiles, _ = resolver.resolve(inventory, reqs, [])
        self.assertGreater(len(profiles), 0)
        # Model B (empirical) MUST defeat Model A (unverified unknown)
        self.assertEqual(profiles[0].model.id, "model-empirical")

if __name__ == "__main__":
    unittest.main()
