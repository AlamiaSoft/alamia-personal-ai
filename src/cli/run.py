import argparse
import uuid
from ..discovery.inventory import InventoryBuilder
from ..resolution.resolver import ExecutionProfileResolver
from ..resolution.task_analyzer import TaskAnalyzer
from ..resolution.preflight import PreflightEngine
from ..adapters.agent_zero.api_bridge import APIBridge
from ..domain.contract.runtime_adapter import ExecuteRequest

def main():
    parser = argparse.ArgumentParser(description="AgentHost Run - Execute a task")
    parser.add_argument("prompt", type=str, help="The task prompt to execute")
    args = parser.parse_args()

    print(f"=== AgentHost Task Execution ===")
    print(f"Task: {args.prompt}\n")
    
    try:
        # 1. Discover
        builder = InventoryBuilder()
        inventory = builder.build()
        
        # 2. Analyze
        analyzer = TaskAnalyzer()
        reqs = analyzer.analyze(args.prompt)
        
        # 3. Resolve
        resolver = ExecutionProfileResolver()
        profiles, explain = resolver.resolve(inventory, reqs, [])
        
        if not profiles:
            print("[FAIL] No valid execution profile found for this task.")
            for m, r in explain.items():
                print(f"  {m}: {r}")
            return
            
        selected_profile = profiles[0]
        print(f"[RESOLVED] Selected Model: {selected_profile.model.id}")
        
        # 4. Preflight
        preflight = PreflightEngine()
        result = preflight.run_task_preflight(selected_profile, reqs)
        if not result.passed:
            print("[FAIL] Preflight checks failed:")
            for reason in result.reasons:
                print(f"  - {reason}")
            return
            
        print("[PASS] Preflight successful. Executing...\n")
        
        # 5. Execute
        bridge = APIBridge()
        ctx_id = str(uuid.uuid4())
        exe_req = ExecuteRequest(context_id=ctx_id, message=args.prompt)
        
        exe_res = bridge.send_message(exe_req)
        
        if exe_res.success:
            print(f"Agent Zero Reply: {exe_res.response}")
        else:
            print("[ERROR] Execution failed.")
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
