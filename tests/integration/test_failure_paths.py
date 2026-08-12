import unittest
import sys
import os
from unittest.mock import patch

from src.discovery.inventory import InventoryBuilder
from src.resolution.resolver import ExecutionProfileResolver
from src.resolution.task_analyzer import TaskAnalyzer
from src.resolution.preflight import PreflightEngine
from src.domain.schemas.task import TaskRequirements
from src.domain.errors import PreflightFailedError

class TestFailurePaths(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

    @patch('src.discovery.os_scanner.OSScanner.check_docker_daemon')
    def test_docker_missing(self, mock_docker):
        mock_docker.return_value = False
        builder = InventoryBuilder()
        inventory = builder.build()
        self.assertFalse(inventory.os_environment["docker_running"])
        
        resolver = ExecutionProfileResolver()
        reqs = TaskRequirements()
        profiles, explain = resolver.resolve(inventory, reqs, [])
        
        # We expect no profiles resolved because Docker is missing
        self.assertEqual(len(profiles), 0)
        self.assertIn("Excluded: Docker not running.", explain.get("agent_zero", ""))

    @patch('src.discovery.model_scanner.ModelScanner.scan_ollama')
    def test_ollama_offline(self, mock_scan):
        mock_scan.return_value = []
        builder = InventoryBuilder()
        inventory = builder.build()
        # Ensure no local models are returned
        local_models = [m for m in inventory.models if m.provider.type == "local"]
        self.assertEqual(len(local_models), 0)
        
    def test_preflight_vram_exceeded(self):
        builder = InventoryBuilder()
        inventory = builder.build()
        
        # Mocking a small hardware footprint
        inventory.hardware.vram_gb = 2.0
        
        # We assume builder found models, let's force a model to require 16GB
        if inventory.models:
            model = inventory.models[0]
            model.hardware.vram_required_gb = 16.0
            
            resolver = ExecutionProfileResolver()
            reqs = TaskRequirements()
            profiles, explain = resolver.resolve(inventory, reqs, [])
            
            # Since VRAM is insufficient, the resolver should exclude it
            # We assert that the model is excluded and explanation mentions VRAM
            found = False
            for p in profiles:
                if p.model.id == model.id:
                    found = True
            self.assertFalse(found)
            self.assertIn("VRAM required", explain.get(model.id, ""))

if __name__ == '__main__':
    unittest.main()
