import argparse
import os
from ..discovery.inventory import InventoryBuilder
from ..domain.errors import AgentHostError
from ..cli.formatter import ErrorFormatter

def main():
    parser = argparse.ArgumentParser(description="AgentHost Setup Wizard")
    parser.parse_args()

    print("=== AgentHost Setup Wizard ===\n")
    
    print("1. Cloud Provider Configuration")
    print("   AgentHost can fall back to cloud providers if your local hardware is insufficient.")
    groq_key = input("   Enter your Groq API Key (or press Enter to skip): ").strip()
    openai_key = input("   Enter your OpenAI API Key (or press Enter to skip): ").strip()
    
    env_lines = []
    enabled_providers = ["ollama"]
    
    if groq_key:
        env_lines.append(f"GROQ_API_KEY={groq_key}")
        enabled_providers.append("groq")
    if openai_key:
        env_lines.append(f"OPENAI_API_KEY={openai_key}")
        enabled_providers.append("openai")
        
    if env_lines:
        env_lines.append("AGENTHOST_MODE=cloud_hybrid")
        env_lines.append(f"AGENTHOST_ENABLED_PROVIDERS={','.join(enabled_providers)}")
        with open(".env", "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(env_lines) + "\n")
        print("   [OK] API Keys and cloud hybrid configuration stored in .env\n")
    else:
        env_lines.append("AGENTHOST_MODE=local")
        env_lines.append("AGENTHOST_ENABLED_PROVIDERS=ollama")
        with open(".env", "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(env_lines) + "\n")
        print("   [OK] Local-only mode enabled and persisted in .env\n")

    print("2. Environment Verification")
    builder = InventoryBuilder()
    try:
        inventory = builder.build()
        
        # Verify Docker
        if inventory.os_environment.get("docker_running", False):
            print("   [OK] Docker connection verified.")
        else:
            print("   [WARN] Docker daemon is not running. Agent Zero execution will fail.")
            
        local_models = [m for m in inventory.models if m.provider.type == "local"]
        cloud_models = [m for m in inventory.models if m.provider.type == "cloud"]
        
        print(f"   [OK] Ollama available ({len(local_models)} local models discovered).")
        if cloud_models:
            print(f"   [OK] Cloud providers enabled ({len(cloud_models)} cloud models discovered).\n")
        else:
            print("   [--] Cloud providers: Disabled (Local-only mode active).\n")
            
        print("Setup complete. AgentHost is ready to accept tasks.")
    except Exception as e:
        # Format friendly errors if things blow up
        err = AgentHostError("SetupFailed", str(e), action="Check your environment and try again.", is_fatal=True)
        print("\n" + ErrorFormatter.format_error(err))
        exit(1)

if __name__ == "__main__":
    main()
