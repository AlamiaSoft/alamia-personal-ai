# AgentHost Implementation Backlog & DAG Matrix

This backlog is structured into 6 sequential sprints, mapped directly to the task dependency graph defined in [02-dag-implementation-plan.md](file:///f:/Playgrounds/alamia-personal-ai/.ai/transient/backlog/02-dag-implementation-plan.md).

---

## Sprint Roadmap & Task Matrix

### Sprint 1: Domain Schemas & Contracts (Phase 0) [COMPLETED]
- `[x]` **`TASK-1.1`**: Error Taxonomy & Base Types (`src/domain/errors`)
- `[x]` **`TASK-1.2`**: ModelProfile & Capability Schemas (`src/domain/schemas/model`)
- `[x]` **`TASK-1.3`**: Hardware & Tool Profile Schemas (`src/domain/schemas/hardware`)
- `[x]` **`TASK-1.4`**: ExecutionProfile & TaskRequirements Schemas (`src/domain/schemas/execution`)
- `[x]` **`TASK-1.5`**: RuntimeAdapter Interface & Mock Adapter (`src/domain/contract/runtime_adapter`)

### Sprint 2: Host Discovery Engine (Phase 1) [COMPLETED]
- `[x]` **`TASK-2.1`**: Hardware & OS Scanner (`src/discovery/hardware_scanner`)
- `[x]` **`TASK-2.2`**: Ollama & Cloud Model Scanner (`src/discovery/model_scanner`)
- `[x]` **`TASK-2.3`**: Inventory Builder & `agenthost scan` CLI (`src/cli/scan`)
- `[x]` **`TASK-2.4`**: Host Doctor & `agenthost doctor` CLI (`src/cli/doctor`)

### Sprint 3: Agent Zero Runtime Adapter (Phase 2) [COMPLETED]
- `[x]` **`TASK-3.1`**: Docker Container Lifecycle Manager (`src/adapters/agent_zero/container`)
- `[x]` **`TASK-3.2`**: Agent Zero REST & WS Bridge (`src/adapters/agent_zero/api_bridge`)
- `[x]` **`TASK-3.3`**: Journal & Log Extractor (`src/adapters/agent_zero/journal`)
- `[x]` **`TASK-3.4`**: Test Suite (`tests/integration/test_agent_zero_adapter`)

### Sprint 4: The Resolver Engine (Phase 3) [COMPLETED]
- `[x]` **`TASK-4.1`**: Task Analyzer (`src/resolution/task_analyzer`)
- `[x]` **`TASK-4.2`**: Tool Injector (`src/resolution/tool_selector`)
- `[x]` **`TASK-4.3`**: Execution Profile Resolver (`src/resolution/resolver`)

### Sprint 5: Preflight Engine (Phase 4) [COMPLETED]
- `[x]` **`TASK-5.1`**: Preflight validation per Execution Profile (`src/resolution/preflight`)

### Sprint 6: CLI UX & Integration (Phase 5) [COMPLETED]
- `[x]` **`TASK-6.1`**: Setup Wizard `agenthost setup` (`src/cli/setup`)
- `[x]` **`TASK-6.2`**: Main execution entrypoint `agenthost run` (`src/cli/run`)

---

## Phase V: V0.1 Product Validation & Hardening Roadmap

### Sprint V1: E2E Happy Path & Onboarding Validation [COMPLETED]
- `[x]` **`TASK-V1.1`**: Live Windows E2E Happy Path Test (`tests/e2e/test_happy_path_live.py`)
- `[x]` **`TASK-V1.2`**: Clean Machine Onboarding Benchmark (`tests/e2e/test_clean_onboarding.py`)

### Sprint V2: Failure-Path Hardening & Friendly Error Formatting [COMPLETED]
- `[x]` **`TASK-V2.1`**: 17-Point Failure Scenario Test Suite (`tests/integration/test_failure_paths.py`)
- `[x]` **`TASK-V2.2`**: CLI User-Friendly Error & Alternative Formatter (`src/cli/formatter.py`)

### Sprint V3: Empirical Evidence Fixtures & Capability Safety [COMPLETED]
- `[x]` **`TASK-V3.1`**: Empirical Capability Regression Fixtures (`tests/fixtures/empirical_capabilities.json`)
- `[x]` **`TASK-V3.2`**: Strict UNKNOWN Capability Safety & Penalty Rules (`src/domain/scoring.py`)

### Sprint V4: Explainable Recommendation Engine [COMPLETED]
- `[x]` **`TASK-V4.1`**: `agenthost recommend` CLI & Explainability Engine (`src/cli/recommend.py`)

### Sprint V5: Architectural Boundary & Decoupling Audit [COMPLETED]
- `[x]` **`TASK-V5.1`**: Multi-Runtime Decoupling & MockRuntimeAdapter Test (`tests/unit/test_runtime_decoupling.py`)
- `[x]` **`TASK-V5.2`**: ModelProvider Abstraction Boundary Audit (`src/domain/contract/model_provider.py`)

### Sprint V6: System Audit, Scorecard & Validation Report [COMPLETED]
- `[x]` **`TASK-V6.1`**: Security, Network & Windows Path Audit
- `[x]` **`TASK-V6.2`**: Benchmark Scorecard & Final GO/NO-GO Report (`docs/agenthost-v0.1-validation-report.md`)

