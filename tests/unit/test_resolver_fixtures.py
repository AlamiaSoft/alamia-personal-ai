import unittest
import json
import os
import sys

from src.discovery.inventory import HostInventory
from src.domain.schemas.hardware import HardwareProfile
from src.domain.schemas.model import ModelProfile, ProviderInfo, HardwareRequirements, Capabilities, Context, Economics, Limits, Evidence
from src.resolution.resolver import ExecutionProfileResolver
from src.domain.schemas.task import TaskRequirements

class TestResolverFixtures(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
        fixture_path = os.path.join(os.path.dirname(__file__), '../fixtures/empirical_capabilities.json')
        with open(fixture_path, 'r') as f:
            self.fixtures = json.load(f)["models"]

    def _create_inventory(self, model_id: str, multi_tool: bool, confidence: float) -> HostInventory:
        model = ModelProfile(
            id=model_id,
            provider=ProviderInfo(id="mock", type="local"),
            hardware=HardwareRequirements(vram_required_gb=2.0),
            capabilities=Capabilities(coding=0.9, reasoning=0.9, tool_calling=1.0 if multi_tool else 0.1, vision=0.0),
            context=Context(window=8192),
            economics=Economics(cost_per_1m_input=0, cost_per_1m_output=0),
            limits=Limits(tpm=None),
            evidence=Evidence(source="empirical", tested=True, confidence=confidence)
        )
        hw = HardwareProfile(cpu_cores=8, ram_gb=32.0, gpu_model="Mock", vram_gb=16.0, disk_space_gb=100.0)
        return HostInventory(hardware=hw, os_environment={"docker_running": True}, models=[model])

    def test_qwen_rejected_for_multitool(self):
        # Qwen known to fail multi_tool
        qwen_fixture = next(m for m in self.fixtures if m["id"] == "qwen:7b")
        inv = self._create_inventory("qwen:7b", qwen_fixture["known_capabilities"]["multi_tool"], qwen_fixture["confidence"])
        
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(browser=True) # Browser requires multi-tool usually
        profiles, explain = resolver.resolve(inv, reqs, [])
        
        # We want to ensure it scores very low or is flagged. With current logic, its score should be extremely low.
        score = profiles[0].reliability_score if profiles else 0
        self.assertLess(score, 0.5, "Qwen should not be confidently recommended for multi-tool tasks")

if __name__ == '__main__':
    unittest.main()
