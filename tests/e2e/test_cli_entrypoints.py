import unittest
import subprocess
import sys
import os

class TestCLIEntrypoints(unittest.TestCase):
    """
    Subprocess integration tests that execute actual python -m src.cli.<command>
    entrypoints to prevent import errors, broken contracts, or syntax crashes.
    """
    def setUp(self):
        self.env = os.environ.copy()
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    def _run_cli(self, module_name: str, args: list = None, input_str: str = None) -> subprocess.CompletedProcess:
        cmd = [sys.executable, "-m", f"src.cli.{module_name}"] + (args or [])
        res = subprocess.run(
            cmd,
            input=input_str,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.root_dir,
            env=self.env,
            timeout=15
        )
        return res

    def test_cli_scan(self):
        res = self._run_cli("scan")
        self.assertEqual(res.returncode, 0, f"src.cli.scan failed: {res.stderr}")
        self.assertIn("models", res.stdout.lower())

    def test_cli_doctor(self):
        res = self._run_cli("doctor")
        self.assertEqual(res.returncode, 0, f"src.cli.doctor failed: {res.stderr}")
        self.assertIn("agenthost doctor", res.stdout.lower())

    def test_cli_recommend(self):
        res = self._run_cli("recommend", ["write a python script"])
        self.assertEqual(res.returncode, 0, f"src.cli.recommend failed: {res.stderr}")
        self.assertIn("agenthost recommendation engine", res.stdout.lower())

    def test_cli_setup(self):
        # Simulate pressing Enter for both API key prompts
        res = self._run_cli("setup", input_str="\n\n")
        self.assertEqual(res.returncode, 0, f"src.cli.setup failed: {res.stderr}")
        self.assertIn("agenthost setup wizard", res.stdout.lower())
        self.assertIn("setup complete", res.stdout.lower())

    def test_cli_run(self):
        res = self._run_cli("run", ["hello world"])
        # Should not crash with ImportError or syntax error even if Agent Zero container is down
        self.assertNotIn("ImportError", res.stderr)
        self.assertNotIn("ModuleNotFoundError", res.stderr)
        self.assertNotIn("Traceback", res.stderr)

if __name__ == "__main__":
    unittest.main()
