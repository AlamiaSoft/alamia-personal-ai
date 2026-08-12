# AgentHost Architecture Plan (Phase L) — v0.1 Specification

**Evidence base:** `docs/agent-zero-evaluation.md`, `docs/agent-zero-capability-matrix.md`, `docs/agent-zero-installation.md`, `docs/agent-zero-security.md`, `docs/model-bottleneck-investigation.md`, `artifacts/*.json`, `docs/feedback/*.md`.

**Principle:** AgentHost is the product; runtimes are replaceable infrastructure. Agent Zero is adopted (with constraints) as the first runtime. AgentHost never depends on Agent Zero internals outside its adapter.

---

## 1. Target Structure (Revised per feedback-03.md)

```text
agent-host/
├── discovery/               # Resource discovery
│   ├── hardware/            # CPU/GPU/RAM/disk, VRAM
│   ├── os/                  # OS version, WSL, Docker availability
│   ├── environment/         # Installed tools, PATH, env vars
│   ├── runtimes/            # Runtime registry + discovery
│   ├── models/              # Model registry + discovery
│   └── tools/               # Tool registry + capability mapping
├── knowledge/               # Structured profiles + evidence
│   ├── runtime-profiles/    # Runtime capability profiles
│   ├── model-profiles/      # Model capability profiles (with evidence + confidence)
│   ├── capability-profiles/ # Capability taxonomy + evidence
│   └── evidence/            # Empirical test results, benchmarks
├── resolution/              # Decision engine
│   ├── task-analyzer/       # Deterministic task capability classification
│   ├── tool-selector/       # Capability-driven tool injection
│   ├── execution-profile-resolver/  # Composite resolver (runtime+model+hardware+tools)
│   └── preflight/           # Two-level preflight (profile + task)
├── execution/               # Runtime mediation
│   ├── contract/            # RuntimeAdapter interface
│   ├── adapters/            # Agent Zero adapter + future
│   └── session/             # Runtime lifecycle + session mgmt
├── security/                # Permissions, secrets, sandbox, audit
└── interface/               # User-facing
    ├── cli/                 # agenthost scan/doctor/setup/run
    ├── local-api/           # REST + WebSocket + SSE
    └── events/              # Event stream for UI
```

---

## 2. Three Core Abstractions (Per feedback-03.md)

### 2.1 Runtime (Provider of Candidates)
```text
Runtime Registry
  ├── Agent Zero
  ├── OpenJarvis
  └── Future...
```
Each runtime provides: lifecycle (install/start/stop/restart), health, execute, stream, logs, diagnostics.

### 2.2 Model (Provider of Candidates)
```text
Model Registry
  ├── Ollama models (local)
  ├── OpenRouter models (cloud)
  ├── Groq models (cloud)
  └── Future...
```
Each model provides: `ModelProfile` with capabilities, hardware requirements, economics, limits, evidence, confidence.

### 2.3 Execution Profile (Fundamental Unit)
```text
Execution Profile Resolver
  │
  ▼
┌────────────────────────────────────────┐
│ Execution Profile                      │
│   Runtime                              │
│   Model                                │
│   Hardware constraints                 │
│   Tools (capability-driven subset)     │
│   Mode (local / cloud / hybrid)        │
│   Capabilities                         │
│   Cost estimate                        │
│   Privacy posture                      │
│   Reliability                          │
└────────────────────────────────────────┘
```
**Same runtime + different model = completely different agent capability.**

Example profiles:
```yaml
# Local Qwen 14B
runtime: agent-zero
model: ollama/qwen2.5-coder:14b
mode: local
capabilities:
  reasoning: medium
  coding: strong
  tool_calling: weak
  browser: unavailable

# Hybrid Cloud+Local
runtime: agent-zero
model: groq/llama-3.3-70b-versatile + ollama/qwen2.5-coder:14b
mode: hybrid
capabilities:
  reasoning: strong
  tool_calling: strong
  browser: strong
```

---

## 3. Runtime Contract (Phase F — Minimum, Evidence-Based)

```text
interface RuntimeAdapter:
    discover() -> RuntimeInfo
    install()  -> InstallResult
    configure(cfg: RuntimeConfig)    # presets/.env/settings, restart-aware
    start() / stop() / restart()
    health()   -> HealthStatus
    capabilities() -> CapabilitySet
    models()   -> ModelList
    execute(req) -> ExecuteResult
    stream(req) -> EventStream
    cancel(ctx_id)
    logs(ctx_id) -> Journal
    diagnostics() -> Diagnostics
```

**Excluded:** `metrics()` (no endpoint), `skills()`/`tools()` (static metadata).

**Agent Zero v2.8 Adapter Facts:**
- Lifecycle: `docker run` with name + version-pinned digest + named volume
- Config: write `usr/plugins/_model_config/presets.yaml` + `config.json`; set UI credentials; store derived `X-API-KEY` token in vault
- Chat: `POST /api/api_message` (context_id, message, attachments, project_name, lifetime_hours); headers `X-API-KEY`
- Journal: `GET/POST /api/api_log_get`; files: `api_files_get`; reset/terminate endpoints verified
- Streaming: socket.io v4 WS (engine.io handshake); REST is request/response
- Version detection: image digest + container `git describe` (v2.8 observed)

---

## 4. Model Profile Schema (Facts + Evidence + Confidence)

```yaml
model:
  id: "ollama/deepseek-r1:14b"
  provider:
    id: "ollama"
    type: "local"
  hardware:
    vram_required_gb: 9
    ram_required_gb: 24
  capabilities:
    coding: 0.8
    reasoning: 0.85
    tool_calling: 0.40
    vision: 0.0
  context:
    window: 32768
  economics:
    cost_per_1m_input: 0
    cost_per_1m_output: 0
  limits:
    tpm: null
  evidence:
    source: "empirical"
    tested: true
    test_suite: "agenthost-a0-v0.1"
    confidence: 0.98   # Current machine test
```

**Confidence Scoring:**
```text
Vendor metadata        0.40
Community benchmark    0.55
AgentHost benchmark    0.90
Current machine test   0.98
```
Effective capability = `capability_score × evidence_confidence`.

---

## 5. Capability Taxonomy (Capability Profiles)

```yaml
capability:
  name: "tool_calling"
  description: "Ability to emit valid JSON tool calls in multi-turn agentic workflows"
  evidence_sources: ["agenthost-benchmark", "vendor-metadata"]
  measurement: "0.0 - 1.0"
  
task_requirements:
  - "browser"
  - "filesystem"
  - "code_execution"
  - "long_context"
  - "vision"
  - "autonomy"
  - "cloud_allowed"
  - "privacy_constraint"
  - "cost_constraint"
```

---

## 6. Deterministic Task Analyzer (v0.1)

```text
task
  ▼
requires browser?        → YES/NO
requires filesystem?     → YES/NO
requires code?           → YES/NO
requires long context?   → YES/NO
requires vision?         → YES/NO
requires autonomy?       → YES/NO
requires cloud?          → YES/NO
privacy constraint?      → YES/NO
cost constraint?         → YES/NO
```

Output: `TaskRequirements` object consumed by Execution Profile Resolver.

---

## 7. Capability-Driven Tool Injection

**Instead of:** Agent sees ALL tools → LLM  
**AgentHost does:**  
```text
User task
  ▼
Required capabilities
  ▼
Required tools
  ▼
Tool subset
  ▼
Runtime
  ▼
Model
```

Example:
```text
"Summarize this PDF"
Required: ✓ filesystem, ✓ document extraction
Not required: ✗ browser, ✗ shell, ✗ MCP, ✗ email, ✗ Git, ✗ database
```
Effect: Smaller prompt → lower tokens → lower cost → smaller model requirement → more hardware compatibility.

---

## 8. Two-Level Preflight

### 8.1 Profile Preflight (Expensive, Rare)
Run when: selecting profile, installing runtime, changing models, changing tools, machine conditions change
```text
hardware
runtime
model
tools
configuration
capabilities
```

### 8.2 Task Preflight (Cheap, Every Request)
```text
required capabilities
  ▼
selected profile
  ▼
compatible?
  ▼
token/quota state?
  ▼
RUN
```
Don't rediscover the entire machine before every request.

---

## 9. Estimated Input-Token Budget (Not a Constant)

```text
estimated_input_tokens =
    system_prompt
  + profile_prompt
  + selected_tools
  + memory_context
  + conversation_context
  + attachments
```
Not: `A0_MIN_TOKENS = 11300`. The ~11.3k is the **estimated baseline for Agent Zero's default fresh-turn construction under the tested configuration**.

---

## 10. Deterministic Execution Profile Resolver

**Inputs:** Hardware Inventory + Runtime Registry + Model Registry + Tool Registry + TaskRequirements

**Algorithm:**
1. Filter runtimes by hardware compatibility (Docker, WSL, VRAM)
2. Filter models by hardware fit (VRAM ≥ requirement) + capability requirements (tool_calling ≥ threshold)
3. Generate candidate execution profiles: (runtime, model, mode) combinations
4. Score each candidate:
   - Capability fit (weighted by evidence confidence)
   - Hardware fit (VRAM headroom, RAM)
   - Cost (local=0, cloud=cost_per_token × estimated_tokens)
   - Privacy (local > cloud)
   - Reliability (evidence confidence)
5. Return ranked profiles + preflight result (PASS/FAIL with reasons)

**Explainability Requirement:** Every decision must be explainable to the user:
```text
Selected Agent Zero because:
  ✓ Docker available
  ✓ Runtime capability score: 8.6
  ✓ Browser capability required
  ✓ MCP available
  ✓ Best compatible runtime discovered

Selected Llama 3.3 70B because:
  ✓ Tool calling verified
  ✓ Strong reasoning
  ✓ Browser-capable
  ⚠ Cloud inference
  ⚠ TPM constraint (12k TPM)

Selected Hybrid profile because:
  ✓ Local Qwen 14B covers 80% of workload
  ✓ Cloud fallback for agentic tasks
```

---

## 11. Security Defaults (Phase J)

```text
Read       → allowed
Write      → confirmation
Execute    → confirmation
External   → confirmation
Destructive → confirmation + audit
```
- Install flow: generate random UI credentials → store token in vault → bind port to loopback only
- Never forward secrets to runtime except during configure(); redact in all logs/events
- A0 CLI/host-file access: only via explicit grant wizard
- Audit: every AgentHost→runtime call logged with user, action, result

---

## 12. Revised Delivery Order (Phases 0–6)

### Phase 0 — Contract + Schemas (No Runtime Implementation)
```text
RuntimeAdapter
ModelProfile
Capability
HardwareProfile
ExecutionProfile
TaskRequirements
PreflightResult
ToolProfile
Evidence/Confidence
```

### Phase 1 — Host Discovery
```text
agenthost scan
agenthost doctor
```
Produces:
```text
environment.json
hardware.json
runtime-inventory.json
model-inventory.json
tool-inventory.json
```

### Phase 2 — Agent Zero Adapter
```text
install, configure, start, stop, restart, health, execute, logs, diagnostics
```
Only Agent Zero v2.8 (Docker + REST + WS + MCP + A2A + journal).

### Phase 3 — Model Registry
```text
Ollama discovery (first)
+ one cloud provider (Groq or OpenRouter)
```
**Ollama + one cloud provider is enough for v0.1.**

### Phase 4 — Execution Profile Resolver
```text
hardware + runtime + models + tools + requirements → profile
```
Implements the resolver algorithm with explainable output.

### Phase 5 — Preflight
Two-level preflight:
- Profile preflight (on install/change)
- Task preflight (per-request)

### Phase 6 — CLI UX
```text
agenthost setup
```
The "magic command" that runs scan → recommend → install → configure → preflight → run.

---

## 13. First Product Experience (Target)

```powershell
irm https://agenthost.ai/install.ps1 | iex
```
```text
Welcome to AgentHost.
I'm going to inspect your computer and build the best AI configuration available to you.

✓ Windows detected
✓ NVIDIA GPU detected
✓ 32 GB RAM
✓ Docker detected
✓ Ollama detected
Found 2 local models.
Found 1 compatible agent runtime.

Recommended setup:
┌─────────────────────────────────────┐
│ AgentHost Personal                  │
│ Agent: Agent Zero                   │
│ Local model: Qwen 14B               │
│ Cloud fallback: ...                 │
│ Mode: Hybrid                        │
│ Privacy: Local-first                │
│ Estimated monthly cost: ~$X         │
└─────────────────────────────────────┘
[ Accept ]
```

---

## 14. Non-Goals for v0.1

- No Laravel control plane
- No dashboard / marketplace / billing / telemetry
- No multi-runtime orchestration (single active runtime)
- No advanced skills marketplace
- No cloud sync / device management
- No LLM-based task analyzer (deterministic only)
- No multi-user / auth system
- No OpenRouter + Groq + Anthropic + OpenAI + Gemini simultaneously (Ollama + one cloud)

---

## 15. Test Strategy

- Fixtures from completed A0 evaluation (`artifacts/*.json`)
- Deterministic resolver tests with known hardware profiles
- Contract tests for RuntimeAdapter
- Preflight tests (profile + task)
- Confidence scoring verification
- Capability-driven tool injection verification

---

## 16. Error Taxonomy

```text
DISCOVERY_ERROR        # Hardware/runtime/model discovery failed
CONFIGURATION_ERROR    # Profile/runtime/model config invalid
PREFLIGHT_FAILED       # Preflight check failed (with reasons)
RUNTIME_UNAVAILABLE    # Runtime not installed/healthy
MODEL_UNAVAILABLE      # Model not available (local/cloud)
CAPABILITY_MISMATCH    # Task requirements > profile capabilities
QUOTA_EXCEEDED         # Provider TPM/cost limits
RUNTIME_ERROR          # Runtime returned error (mapped)
```

---

**End of AgentHost v0.1 Specification.**  
This synthesizes all evidence from the Agent Zero evaluation, model bottleneck investigation, and three rounds of architectural feedback into an implementable contract. The next step is to begin Phase 0 implementation: define the TypeScript/Python schemas and contracts.