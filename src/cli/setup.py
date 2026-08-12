import argparse
from ..discovery.inventory import InventoryBuilder
from ..resolution.resolver import ExecutionProfileResolver
from ..resolution.task_analyzer import TaskAnalyzer
from ..resolution.tool_selector import ToolSelector

def main():
    parser = argparse.ArgumentParser(description="AgentHost Setup Wizard")
    parser.parse_args()

    print("=== AgentHost Setup Wizard ===")
    print("1. Scanning Environment...")
    builder = InventoryBuilder()
    try:
        inventory = builder.build()
        print(f"   Found {len(inventory.models)} models.")
        
        print("\n2. Initializing Resolver...")
        resolver = ExecutionProfileResolver()
        analyzer = TaskAnalyzer()
        selector = ToolSelector(available_tools=[])
        
        print("\nSetup complete. AgentHost is ready to accept tasks.")
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
