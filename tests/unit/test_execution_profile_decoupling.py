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

    def test_7_structural_ranking_cannot_manufacture_capability_claims(self):
        """Structural ranking must not manufacture capability claims or alter confidence values."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        profiles, _ = resolver.resolve(self.inventory, reqs, [])
        model = profiles[0].model
        self.assertEqual(model.capabilities.coding, 0.0)
        self.assertEqual(model.evidence.confidence, 0.0)
        self.assertFalse(model.evidence.tested)

    def test_8_verified_coding_model_outranks_unverified_structural_candidate(self):
        """An empirically verified coding model must outrank an unverified candidate with large structural context/VRAM."""
        unverified_large = ModelProfile(
            id="ollama/unverified:70b",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=15.0),
            capabilities=Capabilities(),
            context=Context(window=262144),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
        )
        verified_small = ModelProfile(
            id="ollama/verified:7b",
            provider=ProviderInfo(id="ollama", type="local"),
            hardware=HardwareRequirements(vram_required_gb=5.0),
            capabilities=Capabilities(coding=0.95, reasoning=0.90, tool_calling=0.90),
            context=Context(window=32768),
            economics=Economics(),
            limits=Limits(),
            evidence=Evidence(source="empirical", tested=True, confidence=0.90)
        )
        inv = HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[unverified_large, verified_small])
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        
        profiles, _ = resolver.resolve(inv, reqs, [])
        self.assertEqual(profiles[0].model.id, "ollama/verified:7b", "Empirically verified candidate must outrank unverified structural candidate")

    def test_9_unknown_capability_remains_unknown(self):
        """UNKNOWN capability must remain confidence = 0.0 and coding = 0.0."""
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        profiles, _ = resolver.resolve(self.inventory, reqs, [])
        self.assertEqual(profiles[0].model.evidence.confidence, 0.0)

    def test_10_inventory_order_cannot_affect_result_multiple_candidates(self):
        """Inventory ordering cannot affect results across 3 candidate permutations."""
        m1 = ModelProfile(id="m1", provider=ProviderInfo(id="mock", type="local"), hardware=HardwareRequirements(vram_required_gb=2.0), context=Context(window=8192), capabilities=Capabilities(), economics=Economics(), limits=Limits(), evidence=Evidence(confidence=0.0))
        m2 = ModelProfile(id="m2", provider=ProviderInfo(id="mock", type="local"), hardware=HardwareRequirements(vram_required_gb=8.0), context=Context(window=32768), capabilities=Capabilities(), economics=Economics(), limits=Limits(), evidence=Evidence(confidence=0.0))
        m3 = ModelProfile(id="m3", provider=ProviderInfo(id="mock", type="local"), hardware=HardwareRequirements(vram_required_gb=12.0), context=Context(window=131072), capabilities=Capabilities(), economics=Economics(), limits=Limits(), evidence=Evidence(confidence=0.0))
        
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        
        res1, _ = resolver.resolve(HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[m1, m2, m3]), reqs, [])
        res2, _ = resolver.resolve(HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[m3, m1, m2]), reqs, [])
        res3, _ = resolver.resolve(HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[m2, m3, m1]), reqs, [])
        
        self.assertEqual(res1[0].model.id, "m3")
        self.assertEqual(res2[0].model.id, "m3")
        self.assertEqual(res3[0].model.id, "m3")

    def test_11_ties_are_deterministic_without_relying_on_discovery_order(self):
        """Tied structural candidates must rank deterministically regardless of discovery array order."""
        mA = ModelProfile(id="model_A", provider=ProviderInfo(id="mock", type="local"), hardware=HardwareRequirements(vram_required_gb=4.0), context=Context(window=32768), capabilities=Capabilities(), economics=Economics(), limits=Limits(), evidence=Evidence(confidence=0.0))
        mB = ModelProfile(id="model_B", provider=ProviderInfo(id="mock", type="local"), hardware=HardwareRequirements(vram_required_gb=4.0), context=Context(window=32768), capabilities=Capabilities(), economics=Economics(), limits=Limits(), evidence=Evidence(confidence=0.0))
        
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements(code_execution=True)
        
        res1, _ = resolver.resolve(HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[mA, mB]), reqs, [])
        res2, _ = resolver.resolve(HostInventory(hardware=self.hw, os_environment={"docker_running": True}, models=[mB, mA]), reqs, [])
        
        self.assertEqual(res1[0].model.id, res2[0].model.id)

if __name__ == "__main__":
    unittest.main()
