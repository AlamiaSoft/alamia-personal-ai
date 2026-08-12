import unittest
import sys
import os
from unittest.mock import patch
import time

from src.discovery.inventory import InventoryBuilder

class TestCleanOnboarding(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

    @patch('src.discovery.os_scanner.OSScanner.check_docker_daemon')
    @patch('src.discovery.model_scanner.ModelScanner._fetch_ollama_tags')
    def test_clean_machine_simulation(self, mock_fetch_tags, mock_check_docker):
        """
        Simulates a completely clean machine where Docker is not running
        and Ollama is not installed/reachable.
        The onboarding process should gracefully handle this in under 5 mins.
        """
        # Mock clean state
        mock_check_docker.return_value = False
        mock_fetch_tags.return_value = {}
        
        start_time = time.time()
        
        builder = InventoryBuilder()
        inventory = builder.build()
        
        duration = time.time() - start_time
        
        self.assertLess(duration, 300, "Onboarding scan should take less than 5 minutes")
        self.assertFalse(inventory.os_environment.get("docker_running"), "Docker should be marked as not running")
        self.assertEqual(len(inventory.models), 0, "No models should be discovered on clean machine")

if __name__ == '__main__':
    unittest.main()
