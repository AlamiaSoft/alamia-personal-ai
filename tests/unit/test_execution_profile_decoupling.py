import unittest
from typing import List
from src.resolution.resolver import ExecutionProfileResolver
from src.discovery.inventory import HostInventory, HardwareProfile
from src.domain.schemas.task import TaskRequirements
from src.domain.schemas.model import ModelProfile, ProviderInfo, HardwareRequirements, Capabilities, Context, Economics, Limits, Evidence
from src.domain.contract.runtime_adapter import RuntimeAdapter, CapabilitySet, RuntimeInfo, InstallResult, HealthStatus, ModelList, ExecuteResult, Journal, Diagnostics, EventStream
from src.domain.contract.registry import RuntimeRegistry

class CustomBrowserRuntimeAdapter(RuntimeAdapter):
    def discover(self): return RuntimeInfo(version="1.0", is_installed=True, status="ready")
    def install(self): return InstallResult(success=True, logs="")
    def configure(self, cfg): pass
    def start(self): pass
    def stop(self): pass
    def restart(self): pass
    def health(self): return HealthStatus(is_healthy=True, message="ok")
    def capabilities(self):
        return CapabilitySet(
            supported_features=["browser"],
            provides_browser=True,
            provides_code_execution=True,
            provides_filesystem=True,
            requires_native_tool_calling=False
        )
    def models(self): return ModelList(models=[])
    def execute(self, req): return ExecuteResult(success=True, response="ok")
    def stream(self, req): return EventStream()
    def cancel(self, ctx_id): pass
    def logs(self, ctx_id): return Journal(logs=[])
    def diagnostics(self): return Diagnostics(metrics={})

class NoBrowserRuntimeAdapter(RuntimeAdapter):
    def discover(self): return RuntimeInfo(version="1.0", is_installed=True, status="ready")
    def install(self): return InstallResult(success=True, logs="")
    def configure(self, cfg): pass
    def start(self): pass
    def stop(self): pass
    def restart(self): pass
    def health(self): return HealthStatus(is_healthy=True, message="ok")
    def capabilities(self):
        return CapabilitySet(
            supported_features=[],
            provides_browser=False,
            provides_code_execution=True,
            provides_filesystem=True,
            requires_native_tool_calling=False
        )
    def models(self): return ModelList(models=[])
    def execute(self, req): return ExecuteResult(success=True, response="ok")
    def stream(self, req): return EventStream()
    def cancel(self, ctx_id): pass
    def logs(self, ctx_id): return Journal(logs=[])
    def diagnostics(self): return Diagnostics(metrics={})

class StrictNativeToolCallingAdapter(RuntimeAdapter):
    def discover(self): return RuntimeInfo(version="1.0", is_installed=True, status="ready")
    def install(self): return InstallResult(success=True, logs="")
    def configure(self, cfg): pass
    def start(self): pass
    def stop(self): pass
    def restart(self): pass
    def health(self): return HealthStatus(is_healthy=True, message="ok")
    def capabilities(self):
        return CapabilitySet(
            supported_features=[],
            provides_browser=False,
            provides_code_execution=True,
            provides_filesystem=True,
            requires_native_tool_calling=True
        )
    def models(self): return ModelList(models=[])
    def execute(self, req): return ExecuteResult(success=True, response="ok")
    def stream(self, req): return EventStream()
    def cancel(self, ctx_id): pass
    def logs(self, ctx_id): return Journal(logs=[])
    def diagnostics(self): return Diagnostics(metrics={})

class TestExecutionProfileDecoupling(unittest.TestCase):

    def setUp(self):
        RuntimeRegistry.register("browser_runtime", CustomBrowserRuntimeAdapter)
        RuntimeRegistry.register("no_browser_runtime", NoBrowserRuntimeAdapter)
        RuntimeRegistry.register("strict_runtime", StrictNativeToolCallingAdapter)

        self.unknown_model = ModelProfile(
            id="ollama/qwen:7b",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=4.0),
            capabilities=Capabilities(coding=0.0, reasoning=0.0, tool_calling=0.0, vision=0.0),
            context=Context(window=32768),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
        )
        self.hw = HardwareProfile(cpu_cores=8, ram_gb=32.0, gpu_model="Mock GPU", vram_gb=16.0, disk_space_gb=100.0)
        self.inventory = HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[self.unknown_model])

    def test_1_local_model_plus_runtime_with_browser_yields_valid_profile(self):
        """Local model + runtime with browser capability -> valid execution profile."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(browser=True, code_execution=True, filesystem=True)
        
        with unittest.mock.patch.object(RuntimeRegistry, "get_adapter", return_value=CustomBrowserRuntimeAdapter):
            profiles, explain = resolver.resolve(self.inventory, reqs, [])
            self.assertEqual(len(profiles), 1)
            self.assertIn("Browser -> agent_zero runtime", explain[self.unknown_model.id])

    def test_2_local_model_plus_runtime_without_browser_yields_rejection(self):
        """Local model + runtime without browser capability -> rejected."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(browser=True, code_execution=True, filesystem=True)
        
        with unittest.mock.patch.object(RuntimeRegistry, "get_adapter", return_value=NoBrowserRuntimeAdapter):
            profiles, explain = resolver.resolve(self.inventory, reqs, [])
            self.assertEqual(len(profiles), 0)
            self.assertIn("Browser capability required", explain[self.unknown_model.id])

    def test_3_model_unknown_tool_calling_plus_strict_runtime_yields_rejection(self):
        """Model with UNKNOWN tool-calling + runtime requiring native tool-calling -> rejected."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        
        with unittest.mock.patch.object(RuntimeRegistry, "get_adapter", return_value=StrictNativeToolCallingAdapter):
            profiles, explain = resolver.resolve(self.inventory, reqs, [])
            self.assertEqual(len(profiles), 0)
            self.assertIn("requires verified native model tool-calling", explain[self.unknown_model.id])

    def test_4_model_unknown_tool_calling_plus_tool_orchestration_runtime_yields_profile(self):
        """Model with UNKNOWN tool-calling + runtime providing tool orchestration -> not rejected solely for tool-calling."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(browser=True, code_execution=True)
        
        with unittest.mock.patch.object(RuntimeRegistry, "get_adapter", return_value=CustomBrowserRuntimeAdapter):
            profiles, explain = resolver.resolve(self.inventory, reqs, [])
            self.assertEqual(len(profiles), 1)

    def test_5_hello_world_resolution_continues_to_work(self):
        """Existing hello world resolution continues to work cleanly."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True, filesystem=True)
        profiles, explain = resolver.resolve(self.inventory, reqs, [])
        self.assertEqual(len(profiles), 1)

    def test_6_inventory_order_cannot_determine_winner(self):
        """Prove that inventory list order cannot determine the winner when unverified models are resolved."""
        m_small = ModelProfile(
            id="ollama/small:1b",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=1.0),
            capabilities=Capabilities(),
            context=Context(window=32768),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
        )
        m_large = ModelProfile(
            id="ollama/large:14b",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=10.0),
            capabilities=Capabilities(),
            context=Context(window=131072),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
        )
        
        # Order A: Small first, Large second
        inv_a = HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[m_small, m_large])
        # Order B: Large first, Small second
        inv_b = HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[m_large, m_small])
        
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        
        profiles_a, _ = resolver.resolve(inv_a, reqs, [])
        profiles_b, _ = resolver.resolve(inv_b, reqs, [])
        
        self.assertEqual(profiles_a[0].model.id, "ollama/large:14b", "Objective structural fit (131k context, 10GB VRAM) must win regardless of initial list order")
        self.assertEqual(profiles_b[0].model.id, "ollama/large:14b", "Objective structural fit (131k context, 10GB VRAM) must win regardless of initial list order")

if __name__ == "__main__":
    unittest.main()
