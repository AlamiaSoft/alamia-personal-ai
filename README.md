# AgentHost 🤖⚡

**AgentHost** is an **Evidence-Driven Execution Profile Resolver** for local/cloud LLMs and autonomous AI agent runtimes (e.g., [Agent Zero](https://github.com/fr2006/agent-zero)).

Unlike generic model wrappers or LLM routers that rely on hardcoded capability scores or model-name heuristics, AgentHost operates on a strict **Evidence & Provenance Model**. It discovers actual runtime metadata, enforces explicit provider activation contracts, and evaluates task requirements across the entire **Execution Profile** (Runtime + Tools + Model + Hardware).

---

## 🔑 Core Integrity Principles

1. **Evidence over Heuristics**:
   - Model IDs (`coder`, `qwen`, `14b`) are **never** parsed or treated as capability evidence.
   - Capability scores are populated strictly from empirical evidence or provider metadata.
   - `UNKNOWN` capability evidence remains explicitly `UNKNOWN` (`confidence = 0.0`).

2. **Provider Activation Contract**:
   - `API Key Exists ≠ Provider Enabled`.
   - The presence of shell environment variables (e.g., `OPENROUTER_API_KEY`) will **never** silently activate cloud providers unless explicitly enabled via AgentHost configuration (`AGENTHOST_ENABLED_PROVIDERS`).

3. **Execution Profile Decoupling**:
   - Model capabilities are decoupled from runtime/tool capabilities.
   - A task requiring a browser (`requirements.browser = True`) is satisfied if the runtime (e.g., Agent Zero) or attached tools provide browser orchestration—models with unverified native function calling are not falsely rejected.

4. **Structural vs. Empirical Suitability**:
   - **Tier 1 (Empirical Evidence)**: Verified benchmark scores (`confidence > 0.40`).
   - **Tier 2 (Structural Fit)**: Evaluates observed metadata facts (context window size, derived hardware VRAM fit) when empirical evidence is `UNKNOWN`.
   - Unverified candidates are explicitly labeled: `Suitability Status: Best structural candidate -- capability unverified`.

5. **List-Order Neutrality & Deterministic Ties**:
   - Discovery array order in `HostInventory` cannot determine recommendation winners.
   - Tied candidates rank deterministically using multi-key tuple sorting (`score`, `context_window`, `vram_required`, `model_id`).

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python**: 3.10+
- **Docker**: Running Docker Desktop / daemon (required for Agent Zero runtime execution)
- **Local LLM Engine (Optional)**: [Ollama](https://ollama.ai) installed and running locally (`http://127.0.0.1:11434`)

### Setup Wizard

Clone the repository and run the setup wizard:

```bash
# Clone the repository
git clone https://github.com/AlamiaSoft/alamia-personal-ai.git
cd alamia-personal-ai

# Run interactive setup wizard
python -m src.cli.setup
```

The setup wizard will:
- Detect local hardware (RAM, discrete NVIDIA GPU VRAM via `nvidia-smi` / `wmic`).
- Check Docker daemon connectivity.
- Scan for local Ollama models.
- Prompt for operational mode (`Local-only` vs `Cloud-enabled`) and provider API keys (Groq, OpenAI, Anthropic, OpenRouter).
- Persist configuration to `.env`.

---

## 🚀 CLI Commands

AgentHost provides 5 primary CLI entrypoints:

### 1. `setup` — Interactive Onboarding Wizard
```bash
python -m src.cli.setup
```
Configures provider enablement, persists mode preferences, and verifies runtime readiness.

### 2. `scan` — Environment & Model Inventory Discovery
```bash
python -m src.cli.scan
```
Scans system hardware, local runtimes, and active cloud provider APIs. Displays provider-by-provider model counts.

### 3. `doctor` — Diagnostics & Health Inspector
```bash
python -m src.cli.doctor
```
Performs multi-point health checks across Docker daemon, environment configuration, local model readiness, and API endpoints.

### 4. `recommend` — Execution Profile Resolver
```bash
python -m src.cli.recommend "write a python script to scrape a website"
```
Analyzes task requirements, resolves execution profiles against discovered inventory, and outputs transparent recommendations with explicit capability provenance:

```text
AgentHost Recommendation Engine

Recommended configuration

Runtime
  Agent_zero 2.8

Model
  ollama/deepseek-r1:14b

Mode
  Local

Suitability Status
  Best structural candidate -- capability unverified

Why?
  [PASS] Structural Fit Score: 0.59
  [PASS] Browser -> agent_zero runtime
  [PASS] Code execution -> agent_zero runtime
  [PASS] Filesystem -> agent_zero runtime
  [PASS] Coding task -> model capability unverified
  [PASS] Structural fit -> ollama/deepseek-r1:14b
  [PASS] Hardware -> NVIDIA GeForce GTX 1080 Ti (11.0 GB VRAM available)
  [WARN] Capability evidence -> UNKNOWN (0%)

Alternative
  ollama/qwen3.5:4b (Local)

Capability Confidence
  UNKNOWN (0% empirical evidence - structural ranking applied)

Estimated cost
  $0.0 / 1M tokens

Resolved in 0.32s
```

### 5. `run` — Task Execution Runner
```bash
python -m src.cli.run "write a python script to scrape a website"
```
Resolves the optimal execution profile and dispatches task execution to the selected runtime adapter (e.g., Agent Zero container bridge).

---

## 🧪 Testing

Run the full automated test suite (32 unit, integration, and subprocess E2E tests):

```bash
python -m unittest tests/unit/test_execution_profile_decoupling.py tests/unit/test_provider_activation.py tests/unit/test_model_evidence.py tests/unit/test_resolver_fixtures.py tests/unit/test_runtime_decoupling.py tests/integration/test_failure_paths.py tests/e2e/test_cli_entrypoints.py
```

---

## 🏛️ Architecture & Documentation

- [System Architecture](.ai/permanent/architecture/01-system-architecture.md)
- [Implementation Integrity Audit](docs/implementation-integrity-audit.md)
- [End-User Setup Guide](docs/end-user-setup-guide.md)
- [Future Phase Roadmap](docs/future-phases-roadmap.md)

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
