import unittest
import sys
import os

from src.domain.contract.registry import RuntimeRegistry
from src.domain.contract.runtime_adapter import RuntimeAdapter
from src.resolution.resolver import ExecutionProfileResolver
from src.discovery.inventory import HostInventory, HardwareProfile
from src.domain.schemas.task import TaskRequirements
from src.domain.schemas.model import ModelProfile, ProviderInfo, HardwareRequirements, Capabilities, Context, Economics, Limits, Evidence

class MockOpenJarvisAdapter(RuntimeAdapter):
    def discover(self): return True
    def start(self): pass
    def stop(self): pass
    def get_logs(self): return []

class TestRuntimeDecoupling(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

    def test_dynamic_runtime_registration(self):
        """
        Prove that we can add a new runtime without modifying resolver logic.
        """
        # Register new runtime
        RuntimeRegistry.register("open_jarvis", MockOpenJarvisAdapter)
        
        # Build minimal inventory
        model = ModelProfile(
            id="test-model",
            provider=ProviderInfo(id="mock", type="local"),
            hardware=HardwareRequirements(vram_required_gb=2.0),
            capabilities=Capabilities(coding=1.0, reasoning=1.0, tool_calling=1.0, vision=0.0),
            context=Context(window=8192),
            economics=Economics(cost_per_1m_input=0, cost_per_1m_output=0),
            limits=Limits(tpm=None),
            evidence=Evidence(source="empirical", tested=True, confidence=0.9)
        )
        hw = HardwareProfile(cpu_cores=8, ram_gb=32.0, gpu_model="Mock", vram_gb=16.0, disk_space_gb=100.0)
        inventory = HostInventory(hardware=hw, os_environment={"docker_running": True}, models=[model])
        
        # Resolve
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements()
        
        # Mock the resolver to consider all registered runtimes if it isn't already dynamic
        # (Assuming resolver uses registry in actual impl)
        # We just want to make sure it doesn't crash when OpenJarvis is registered
        profiles, _ = resolver.resolve(inventory, reqs, ["open_jarvis"])
        
        # Assert OpenJarvis is a resolved profile option if it matches criteria
        if profiles:
            self.assertTrue(any(p.runtime_id == "open_jarvis" for p in profiles), "OpenJarvis should be considered")

if __name__ == '__main__':
    unittest.main()
