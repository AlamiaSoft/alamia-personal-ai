import unittest
from src.adapters.agent_zero.container import AgentZeroContainer
from src.adapters.agent_zero.api_bridge import APIBridge
from src.adapters.agent_zero.journal import JournalExtractor
from src.domain.contract.runtime_adapter import ExecuteRequest

class TestAgentZeroAdapter(unittest.TestCase):
    def setUp(self):
        self.container = AgentZeroContainer("test-agent-zero")
        self.bridge = APIBridge()
        self.journal = JournalExtractor()

    def test_container_lifecycle(self):
        # MVP test: Ensure it doesn't crash
        self.container.start()
        self.assertFalse(self.container.get_health(), "Should be false since mock container doesn't exist")
        self.container.stop()
        
    def test_api_bridge(self):
        req = ExecuteRequest(context_id="test1", message="Hello", attachments=[])
        res = self.bridge.send_message(req)
        self.assertTrue(res.success)
        self.assertIn("Mock", res.response)

    def test_journal_extractor(self):
        journal = self.journal.extract("test1")
        self.assertGreater(len(journal.logs), 0)
        self.assertIn("Mock", journal.logs[0])

if __name__ == '__main__':
    unittest.main()
