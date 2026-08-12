import argparse
import json
from ..discovery.inventory import InventoryBuilder

def main():
    parser = argparse.ArgumentParser(description="AgentHost Scanner - Discovers host hardware, OS, and models.")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    builder = InventoryBuilder()
    
    try:
        inventory = builder.build()
        if args.json:
            print(inventory.model_dump_json(indent=2))
        else:
            print("=== AgentHost Host Inventory ===")
            print("\n[Hardware]")
            print(f"CPU Cores: {inventory.hardware.cpu_cores}")
            print(f"System RAM: {inventory.hardware.ram_gb} GB")
            print(f"GPU Model: {inventory.hardware.gpu_model}")
            print(f"VRAM: {inventory.hardware.vram_gb} GB")
            print(f"Disk Space: {inventory.hardware.disk_space_gb} GB")
            
            print("\n[Environment]")
            for k, v in inventory.os_environment.items():
                print(f"{k}: {v}")
                
            print(f"\n[Models] ({len(inventory.models)} discovered)")
            for m in inventory.models:
                print(f"- {m.id} (Provider: {m.provider.id}, Type: {m.provider.type})")
                
    except Exception as e:
        print(f"Error during scan: {e}")
        exit(1)

if __name__ == "__main__":
    main()
