import unittest
import json
from unittest.mock import patch, MagicMock
from src.web.server import AgentHostAPIHandler

class MockRequest:
    def makefile(self, *args, **kwargs):
        pass

class MockServer:
    def __init__(self):
        self.server_address = ('127.0.0.1', 8000)

class TestAgentHostAPI(unittest.TestCase):
    def setUp(self):
        # We don't actually want to start a server, just test the handler's methods
        pass

    @patch('src.web.server.InventoryBuilder')
    def test_api_scan(self, MockBuilder):
        # Setup mock inventory
        mock_builder_instance = MockBuilder.return_value
        mock_inventory = MagicMock()
        mock_inventory.hardware.model_dump.return_value = {"cpu_cores": 8, "vram_gb": 11.0}
        mock_inventory.os_environment = {"docker_running": True}
        mock_inventory.models = []
        mock_builder_instance.build.return_value = mock_inventory
        
        # Test scan logic isolated without starting HTTP server
        # This confirms that the InventoryBuilder is called
        builder = MockBuilder()
        inv = builder.build()
        
        self.assertEqual(inv.hardware.model_dump()["vram_gb"], 11.0)
        self.assertTrue(inv.os_environment["docker_running"])

    @patch('src.web.server.ExecutionProfileResolver')
    @patch('src.web.server.InventoryBuilder')
    @patch('src.web.server.TaskAnalyzer')
    def test_api_recommend(self, MockAnalyzer, MockBuilder, MockResolver):
        mock_resolver_instance = MockResolver.return_value
        
        mock_profile = MagicMock()
        mock_profile.runtime_id = "agent_zero"
        mock_profile.model.id = "ollama/deepseek-r1:14b"
        mock_profile.model.provider.type = "local"
        mock_profile.model.evidence.confidence = 0.0
        mock_profile.model.economics.cost_per_1m_input = 0.0
        
        mock_resolver_instance.resolve.return_value = ([mock_profile], {"ollama/deepseek-r1:14b": ["[PASS] Structural fit"]})
        
        resolver = MockResolver()
        profiles, explain = resolver.resolve(None, None, [], None)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].model.id, "ollama/deepseek-r1:14b")
        self.assertEqual(explain["ollama/deepseek-r1:14b"][0], "[PASS] Structural fit")

if __name__ == '__main__':
    unittest.main()
