import unittest
import subprocess
import json
import uuid
import sys
import os

from src.discovery.inventory import InventoryBuilder
from src.resolution.resolver import ExecutionProfileResolver
from src.resolution.task_analyzer import TaskAnalyzer
from src.resolution.preflight import PreflightEngine
from src.adapters.agent_zero.api_bridge import APIBridge
from src.domain.contract.runtime_adapter import ExecuteRequest
from src.domain.schemas.task import TaskRequirements

class TestHappyPathLive(unittest.TestCase):
    def setUp(self):
        # Ensure we are running from project root or add src to path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

    def test_end_to_end_pipeline(self):
        """
        Tests the complete E2E flow:
        discover -> analyze -> resolve -> preflight -> run
        """
        try:
            # 1. Discover
            builder = InventoryBuilder()
            inventory = builder.build()
            self.assertIsNotNone(inventory, "Inventory should not be None")
            self.assertIsNotNone(inventory.hardware, "Hardware profile should be built")
            self.assertIn("docker_running", inventory.os_environment)
            
            # 2. Analyze
            analyzer = TaskAnalyzer()
            reqs = analyzer.analyze("run a simple python script to print hello world")
            self.assertTrue(reqs.code_execution, "Task should require code execution")
            
            # 3. Resolve
            resolver = ExecutionProfileResolver()
            profiles, explain = resolver.resolve(inventory, reqs, [])
            
            # If Docker isn't running or no models, we might not get profiles.
            # For a live happy path test, we expect at least one profile or graceful fallback.
            if not profiles:
                self.skipTest("No profiles resolved (check Docker/Ollama). Skipping execution phase.")
                
            selected_profile = profiles[0]
            self.assertEqual(selected_profile.runtime_id, "agent_zero")
            
            # 4. Preflight
            preflight = PreflightEngine()
            result = preflight.run_task_preflight(selected_profile, reqs)
            self.assertTrue(result.passed, f"Preflight failed: {result.reasons}")
            
            # 5. Execute
            bridge = APIBridge()
            ctx_id = str(uuid.uuid4())
            exe_req = ExecuteRequest(context_id=ctx_id, message="print hello world")
            exe_res = bridge.send_message(exe_req)
            
            self.assertTrue(exe_res.success, "API Bridge execution failed")
            
        except Exception as e:
            self.fail(f"E2E Pipeline failed with exception: {str(e)}")

if __name__ == '__main__':
    unittest.main()
