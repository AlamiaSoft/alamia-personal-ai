import argparse
from ..discovery.inventory import InventoryBuilder

def main():
    parser = argparse.ArgumentParser(description="AgentHost Doctor - Diagnoses host readiness.")
    parser.parse_args()

    print("=== AgentHost Doctor ===")
    print("Running diagnostic checks...\n")
    
    builder = InventoryBuilder()
    
    try:
        inventory = builder.build()
        
        # Check Docker
        if inventory.os_environment.get("docker_running", False):
            print("[PASS] Docker is installed and running.")
        else:
            print("[FAIL] Docker is not running or not accessible.")
            print("       -> Agent Zero requires Docker to isolate environments.")
            print("       -> Ensure Docker Desktop is started and WSL integration is enabled if on Windows.")
            
        # Check VRAM
        vram = inventory.hardware.vram_gb
        if vram is None or vram < 4.0:
            print(f"[WARN] Low VRAM detected (Found: {vram} GB).")
            print("       -> Local models may perform poorly or fail to load.")
            print("       -> Consider hybrid mode with cloud fallback.")
        else:
            print(f"[PASS] VRAM check passed ({vram} GB available).")
            
        # Check Models
        if len(inventory.models) > 0:
            print(f"[PASS] {len(inventory.models)} models found.")
        else:
            print("[WARN] No models discovered.")
            print("       -> Ensure Ollama is running or configure cloud provider keys.")
            
        print("\nDiagnostic complete.")
    except Exception as e:
        print(f"[ERROR] Diagnostic failed during inventory build: {e}")
        exit(1)

if __name__ == "__main__":
    main()
