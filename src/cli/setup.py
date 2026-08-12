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
    if groq_key:
        env_lines.append(f"GROQ_API_KEY={groq_key}")
    if openai_key:
        env_lines.append(f"OPENAI_API_KEY={openai_key}")
        
    if env_lines:
        with open(".env", "a") as f:
            f.write("\n" + "\n".join(env_lines) + "\n")
        print("   [OK] API Keys securely stored in .env\n")
    else:
        print("   [OK] Skipping cloud configuration. Local-only mode enabled.\n")

    print("2. Environment Verification")
    builder = InventoryBuilder()
    try:
        inventory = builder.build()
        
        # Verify Docker
        if inventory.os_environment.get("docker_running", False):
            print("   [OK] Docker connection verified.")
        else:
            print("   [WARN] Docker daemon is not running. Agent Zero execution will fail.")
            
        print(f"   [OK] Scanned environment and found {len(inventory.models)} models.\n")
        
        print("Setup complete. AgentHost is ready to accept tasks.")
    except Exception as e:
        # Format friendly errors if things blow up
        err = AgentHostError("SetupFailed", str(e), action="Check your environment and try again.", is_fatal=True)
        print("\n" + ErrorFormatter.format_error(err))
        exit(1)

if __name__ == "__main__":
    main()
