import unittest
from unittest.mock import patch, MagicMock
import os
import json

from src.config import is_provider_enabled, get_credential, load_agenthost_config
from src.discovery.model_scanner import ModelScanner
from src.discovery.providers.openrouter import OpenRouterProviderAdapter
from src.discovery.providers.groq import GroqProviderAdapter
from src.domain.schemas.model import ModelProfile, ProviderInfo, HardwareRequirements, Capabilities, Context, Economics, Limits, Evidence

class TestProviderActivation(unittest.TestCase):

    def setUp(self):
        # Ensure clean state before each test
        if os.path.exists(".env.bak"):
            os.remove(".env.bak")
        if os.path.exists(".env"):
            os.rename(".env", ".env.bak")

    def tearDown(self):
        if os.path.exists(".env"):
            os.remove(".env")
        if os.path.exists(".env.bak"):
            os.rename(".env.bak", ".env")

    def test_1_os_key_plus_provider_disabled_yields_zero_discovery(self):
        """OS shell has OPENROUTER_API_KEY, but AgentHost config is Local-only -> zero OpenRouter models."""
        with open(".env", "w", encoding="utf-8") as f:
            f.write("AGENTHOST_MODE=local\nAGENTHOST_ENABLED_PROVIDERS=ollama\n")
            
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "os_shell_key"}):
            self.assertFalse(is_provider_enabled("openrouter"))
            self.assertIsNone(get_credential("OPENROUTER_API_KEY", "openrouter"))
            
            adapter = OpenRouterProviderAdapter()
            models = adapter.discover_models()
            self.assertEqual(len(models), 0, "A credential's mere existence in os.environ must NEVER activate a provider")

    def test_2_os_key_plus_provider_enabled_yields_successful_discovery(self):
        """OS shell has OPENROUTER_API_KEY, and AgentHost config explicitly enables openrouter -> discovery succeeds via precedence."""
        with open(".env", "w", encoding="utf-8") as f:
            f.write("AGENTHOST_MODE=cloud_hybrid\nAGENTHOST_ENABLED_PROVIDERS=ollama,openrouter\n")
            
        mock_openrouter_resp = {
            "data": [{"id": "openai/gpt-4o", "context_length": 128000, "pricing": {"prompt": "0.000005", "completion": "0.000015"}}]
        }
        
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "os_shell_key"}):
            self.assertTrue(is_provider_enabled("openrouter"))
            self.assertEqual(get_credential("OPENROUTER_API_KEY", "openrouter"), "os_shell_key")
            
            adapter = OpenRouterProviderAdapter()
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_resp = MagicMock()
                mock_resp.status = 200
                mock_resp.read.return_value = json.dumps(mock_openrouter_resp).encode('utf-8')
                mock_urlopen.return_value.__enter__.return_value = mock_resp
                
                models = adapter.discover_models()
                self.assertEqual(len(models), 1)
                self.assertEqual(models[0].id, "openrouter/openai/gpt-4o")

    def test_3_dotenv_key_plus_provider_disabled_yields_zero_discovery(self):
        """.env key exists for groq, but AGENTHOST_ENABLED_PROVIDERS=ollama -> zero Groq discovery."""
        with open(".env", "w", encoding="utf-8") as f:
            f.write("GROQ_API_KEY=dot_env_key\nAGENTHOST_MODE=local\nAGENTHOST_ENABLED_PROVIDERS=ollama\n")
            
        self.assertFalse(is_provider_enabled("groq"))
        self.assertIsNone(get_credential("GROQ_API_KEY", "groq"))
        
        adapter = GroqProviderAdapter()
        models = adapter.discover_models()
        self.assertEqual(len(models), 0)

    def test_4_provider_enabled_plus_no_credential_yields_zero_models(self):
        """Provider is enabled in config, but no API key exists anywhere -> zero models, no fabrication."""
        with open(".env", "w", encoding="utf-8") as f:
            f.write("AGENTHOST_MODE=cloud_hybrid\nAGENTHOST_ENABLED_PROVIDERS=ollama,groq\n")
            
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(is_provider_enabled("groq"))
            self.assertIsNone(get_credential("GROQ_API_KEY", "groq"))
            
            adapter = GroqProviderAdapter()
            models = adapter.discover_models()
            self.assertEqual(len(models), 0, "No credentials must result in zero models, not fabricated stubs")

    def test_5_local_only_persists_across_fresh_cli_invocations(self):
        """Persisted AGENTHOST_MODE=local in .env guarantees scan_all() returns ONLY local models."""
        with open(".env", "w", encoding="utf-8") as f:
            f.write("AGENTHOST_MODE=local\nAGENTHOST_ENABLED_PROVIDERS=ollama\n")
            
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "os_shell_key", "GROQ_API_KEY": "os_groq_key"}):
            with patch("src.discovery.providers.ollama.OllamaProviderAdapter.discover_models") as mock_ollama:
                mock_ollama.return_value = [
                    ModelProfile(
                        id="ollama/qwen:7b",
                        provider=ProviderInfo(id="ollama", type="local"),
                        hardware=HardwareRequirements(vram_required_gb=4.0),
                        capabilities=Capabilities(),
                        context=Context(window=8192),
                        economics=Economics(),
                        limits=Limits(),
                        evidence=Evidence(source="runtime_metadata", tested=False, confidence=0.0)
                    )
                ]
                
                scanner = ModelScanner()
                all_models = scanner.scan_all()
                self.assertEqual(len(all_models), 1)
                self.assertEqual(all_models[0].provider.type, "local")

    def test_6_scan_does_not_overwrite_existing_config(self):
        """Running ModelScanner.scan_all() must not modify or overwrite existing .env configuration."""
        initial_config = "AGENTHOST_MODE=local\nAGENTHOST_ENABLED_PROVIDERS=ollama\nCUSTOM_SETTING=keep_me\n"
        with open(".env", "w", encoding="utf-8") as f:
            f.write(initial_config)
            
        scanner = ModelScanner()
        with patch("src.discovery.providers.ollama.OllamaProviderAdapter.discover_models", return_value=[]):
            scanner.scan_all()
            
        with open(".env", "r", encoding="utf-8") as f:
            current_config = f.read()
            
        self.assertEqual(current_config, initial_config)

if __name__ == "__main__":
    unittest.main()
