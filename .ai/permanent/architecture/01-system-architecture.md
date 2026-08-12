# AgentHost System Architecture

## 1. Core Mission & Architectural Philosophy

**AgentHost** is a runtime-agnostic personal AI platform and local daemon.

### The Foundational Axiom
> **The user owns the agent experience. The runtime is replaceable infrastructure.**

AgentHost provides a unified, local-first control plane, task analyzer, decision engine (Execution Profile Resolver), and security boundary for operating personal AI agents. It abstracts underlying agent runtimes (such as Agent Zero, OpenJarvis, OpenCode, or custom runtimes) behind a clean, stable contract interface (`RuntimeAdapter`). AgentHost never depends directly on individual runtime implementation details outside its dedicated runtime adapters.

---

## 2. Conceptual System Topology

```text
                               AgentHost Platform
                                       │
                      ┌────────────────┴────────────────┐
                      │                                 │
                Interface Layer                   Security Layer
             (CLI / Local API / SSE)        (Permissions/Vault/Audit)
                      │                                 │
                      └────────────────┬────────────────┘
                                       │
                          Execution Profile Resolver
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
         Resource Discovery       Task Analyzer         Tool Injection
         (Hardware/OS/Models) (Requirements Classifier) (Subset Assembly)
                │                      │                      │
                └──────────────────────┼──────────────────────┘
                                       │
                           RuntimeAdapter Contract
                                       │
               ┌───────────────────────┼───────────────────────┐
               │                       │                       │
      Agent Zero Adapter       OpenJarvis Adapter       Future Adapters
        (Docker/REST/WS)               │                       │
               │                       │                       │
               └───────────────────────┼───────────────────────┘
                                       │
                               Model Providers
                        (Ollama / Cloud Providers)
```

---

## 3. The Core Abstractions

### 3.1 Runtime (Candidate Provider)
A runtime provides execution lifecycle and agent capabilities.
- **Contract Interface**: `RuntimeAdapter`
- **Capabilities**: Lifecycle (`install`, `start`, `stop`, `restart`), `health`, `capabilities`, `models`, `execute`, `stream`, `cancel`, `logs`, `diagnostics`.
- **First Candidate Runtime**: Agent Zero v2.8 (evaluated and adopted with constraints; containerized in Docker, mediated via HTTP/WS APIs).

### 3.2 Model (Candidate Provider)
Models provide intelligence candidates across local engines (Ollama) and cloud services (Groq, OpenRouter, etc.).
- **Model Profile Schema**: Defines VRAM/RAM hardware requirements, capability scores (coding, reasoning, tool_calling, vision), context window, economics, and empirical evidence/confidence ratings.

### 3.3 Execution Profile (The Fundamental Unit)
Agent capability is determined by the composite unit:
$$\text{Execution Profile} = (\text{Runtime}, \text{Model}, \text{Hardware Constraints}, \text{Tools}, \text{Mode})$$

Changing the model on a runtime yields a completely distinct operational profile.

### 3.4 Capability Taxonomy & Confidence Scoring
- Capability scores ($0.0 - 1.0$) are weighted by evidence confidence:
  $$\text{effective\_capability} = \text{capability\_score} \times \text{evidence\_confidence}$$
- Confidence Scale:
  - Vendor metadata: $0.40$
  - Community benchmark: $0.55$
  - AgentHost benchmark: $0.90$
  - Current machine empirical test: $0.98$

---

## 4. Key Subsystems

### 4.1 Resource & Host Discovery (`discovery/`)
Discovers host machine capabilities without assuming pre-existing dependencies:
- **Hardware**: CPU, GPU model, VRAM, RAM, disk headroom.
- **OS & Environment**: OS version, WSL, Docker daemon availability, environment PATH.
- **Runtime & Model Inventories**: Registered runtimes and local/cloud models.

### 4.2 Deterministic Task Analyzer (`resolution/task-analyzer/`)
Classifies task requirements strictly using deterministic rules before LLM invocation:
- Evaluates needs: `browser`, `filesystem`, `code_execution`, `long_context`, `vision`, `autonomy`, `cloud_allowed`, `privacy_constraint`, `cost_constraint`.

### 4.3 Capability-Driven Tool Injection (`resolution/tool-selector/`)
Injects only the minimal required tool subset into the runtime prompt for a given task:
- Prevents bloat from injecting standard all-tool prompt matrices (~11.3k tokens baseline down to minimal sets).
- Reduces input token costs, lowers response latency, and enables smaller local models to execute reliably.

### 4.4 Execution Profile Resolver (`resolution/execution-profile-resolver/`)
Deterministic decision engine that matches host capabilities and task requirements against execution profile candidates:
1. Filters runtimes by hardware/container compatibility.
2. Filters models by VRAM/RAM limits and tool-calling thresholds.
3. Scores and ranks candidate profiles by capability fit, hardware headroom, cost, privacy, and reliability.
4. Outputs explainable rationale for every selection.

### 4.5 Two-Level Preflight (`resolution/preflight/`)
- **Profile Preflight (Heavy)**: Triggered on profile selection, runtime installation, or model/tool configuration change.
- **Task Preflight (Lightweight)**: Runs per request to verify profile state, token budgets, and quota limits.

---

## 5. Security Architecture & Invariants

AgentHost strictly enforces **Least Privilege**:
- **Loopback Binding**: Local API listens exclusively on `127.0.0.1`.
- **Credential Storage**: Randomly generated UI credentials and API keys stored in local secure vault.
- **Consent Tiers**:
  - `Read`: Allowed by default.
  - `Write / Execute / External`: Requires explicit confirmation.
  - `Destructive`: Explicit confirmation + audit logging.
- **Secret Redaction**: API keys and tokens are stripped from logs and diagnostic events.

---

## 6. Architectural Invariants & Non-Goals for v0.1

### Invariants
1. AgentHost operates standalone; it has zero coupling to external control planes or cloud services.
2. Direct access to runtime internals outside `RuntimeAdapter` implementations is prohibited.
3. All resolver decisions must be deterministic and fully explainable.

### Non-Goals for v0.1
- No Laravel control plane.
- No dashboard/marketplace/telemetry cloud services.
- No multi-runtime concurrent orchestration (single active profile execution).
- Deterministic task analyzer only (no LLM classifier in v0.1).
