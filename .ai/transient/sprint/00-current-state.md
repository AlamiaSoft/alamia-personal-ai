# Sprint Current State: WEB UI IMPLEMENTATION PHASE

## Active Sprint Focus
- **Current Sprint**: **SPRINT UI1 (Web API Server & REST Endpoints)**
- **DAG Reference**: [04-web-ui-implementation-dag.md](file:///f:/Playgrounds/alamia-personal-ai/.ai/transient/backlog/04-web-ui-implementation-dag.md)
- **Active Task Node**: `TASK-UI1.1` (Web API Server Core `src/web/server.py`)

---

## Final Deliverables & Verification Criteria Met
- V0.1 Validation Report published recommending GO.
- Empirical regression fixtures and strict UNKNOWN safety rules enforced.
- 17-point failure matrix handled gracefully via new Formatter.
- `agenthost recommend` CLI built.
- Architecture fully decoupled (MockRuntimeAdapter & ModelProvider).
- Security & Path Audits passed.

---

## Future Phase Roadmap (Captured for Later Phase)

### Controlled Empirical Capability Probing System
Transition AgentHost from `BEST STRUCTURAL CANDIDATE (Capability UNKNOWN)` to `BEST VERIFIED CANDIDATE (Capability Confidence Matrix)`.

- **Objective**: Build a controlled probing engine that executes standardized micro-benchmarks against local and cloud models to measure real performance.
- **Evidence Record Schema**:
  - `model_id`: Canonical provider/model string (e.g., `ollama/deepseek-r1:14b`)
  - `digest`: Exact artifact SHA256 checksum
  - `task_category`: Capability category (`coding`, `reasoning`, `tool_use`, `vision`)
  - `probe_version`: Probing suite version string (e.g., `v1.2.0`)
  - `test_result`: Quantitative benchmark result metrics
  - `capability_score`: Measured capability score (`0.00` – `1.00`)
  - `timestamp`: UTC ISO timestamp of empirical run
  - `confidence`: Calculated confidence based on sample size and probe recency
- **Resolver Outcome**:
  - Enables resolver to dynamically transition from `BEST STRUCTURAL CANDIDATE (capability UNKNOWN)` to `BEST VERIFIED CANDIDATE` with measured empirical scores (e.g., `coding confidence: 0.91`, `tool-use confidence: 0.84`).

