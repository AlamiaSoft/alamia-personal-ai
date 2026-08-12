import argparse
import sys
import os
import time

from src.discovery.inventory import InventoryBuilder
from src.resolution.resolver import ExecutionProfileResolver
from src.resolution.task_analyzer import TaskAnalyzer
from src.domain.schemas.user_policy import UserPolicy

def main():
    parser = argparse.ArgumentParser(description="Recommend execution profile")
    parser.add_argument("task", nargs="?", default="general task", help="Task description")
    args = parser.parse_args()

    print("AgentHost Recommendation Engine\n")
    start_time = time.time()
    
    # Discovery
    builder = InventoryBuilder()
    inventory = builder.build()
    
    # Analysis
    analyzer = TaskAnalyzer()
    reqs = analyzer.analyze(args.task)
    
    # Policy (Default for MVP)
    policy = UserPolicy()
    
    # Resolution
    resolver = ExecutionProfileResolver()
    profiles, explainability = resolver.resolve(inventory, reqs, [], policy)
    
    elapsed = time.time() - start_time
    
    if not profiles:
        print("No suitable profile found.")
        print(f"Elapsed: {elapsed:.2f}s")
        sys.exit(1)
        
    top_profile = profiles[0]
    is_verified = top_profile.model.evidence.confidence > 0.40
    
    print("Recommended configuration\n")
    print(f"Runtime\n  {top_profile.runtime_id.capitalize()} 2.8\n")
    print(f"Model\n  {top_profile.model.id}\n")
    print(f"Mode\n  {top_profile.model.provider.type.capitalize()}\n")
    
    if is_verified:
        print("Suitability Status\n  Empirically Verified Capable Candidate\n")
    else:
        print("Suitability Status\n  Best structural candidate -- capability unverified\n")
    
    print("Why?")
    rec_explain = explainability.get(top_profile.model.id, [])
    for reason in rec_explain:
        if "[WARN]" in reason:
            print(f"  {reason}")
        else:
            print(f"  [PASS] {reason}")
    print()
    
    if len(profiles) > 1:
        alt_profile = profiles[1]
        print(f"Alternative\n  {alt_profile.model.id} ({alt_profile.model.provider.type.capitalize()})\n")
    
    if is_verified:
        print(f"Capability Confidence\n  {top_profile.reliability_score * 100:.0f}%\n")
    else:
        print("Capability Confidence\n  UNKNOWN (0% empirical evidence - structural ranking applied)\n")
        
    print(f"Estimated cost\n  ${top_profile.model.economics.cost_per_1m_input} / 1M tokens\n")
    print(f"Resolved in {elapsed:.2f}s")

if __name__ == "__main__":
    main()
