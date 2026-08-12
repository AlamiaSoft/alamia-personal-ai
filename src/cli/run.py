import argparse
import uuid
from ..discovery.inventory import InventoryBuilder
from ..resolution.resolver import ExecutionProfileResolver
from ..resolution.task_analyzer import TaskAnalyzer
from ..resolution.preflight import PreflightEngine
from ..adapters.agent_zero.api_bridge import APIBridge
from ..domain.contract.runtime_adapter import ExecuteRequest
from ..domain.errors import AgentHostError
from ..cli.formatter import ErrorFormatter

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
            err = AgentHostError(
                "NoValidProfile",
                "No valid execution profile found for this task.",
                alternatives=[f"{m}: {r}" for m, r in explain.items()],
                action="Try adjusting task requirements or starting Docker/Ollama daemons."
            )
            print(ErrorFormatter.format_error(err))
            return
            
        selected_profile = profiles[0]
        print(f"[RESOLVED] Selected Model: {selected_profile.model.id}")
        
        # 4. Preflight
        preflight = PreflightEngine()
        result = preflight.run_task_preflight(selected_profile, reqs)
        if not result.passed:
            err = AgentHostError(
                "PreflightFailed",
                "Preflight validation checks failed prior to execution.",
                alternatives=result.reasons,
                action="Resolve preflight resource issues or select a lighter model."
            )
            print(ErrorFormatter.format_error(err))
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
            err = AgentHostError(
                "ExecutionFailed",
                exe_res.response,
                action="Verify Agent Zero API bridge container is active on http://127.0.0.1:5000."
            )
            print(ErrorFormatter.format_error(err))
            
    except Exception as e:
        err = AgentHostError("RuntimeError", str(e), action="Inspect system diagnostics with `python -m src.cli.doctor`.")
        print(ErrorFormatter.format_error(err))

if __name__ == "__main__":
    main()
