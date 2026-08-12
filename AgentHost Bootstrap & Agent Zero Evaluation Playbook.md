# AgentHost Bootstrap & Agent Zero Evaluation Playbook

## 1. Mission

Evaluate **Agent Zero** as the first candidate runtime for a new **runtime-agnostic personal AI platform**, then produce an evidence-based suitability report and a concrete architecture/implementation plan for **AgentHost**.

The goal is **not** to build an Agent Zero wrapper.

The goal is to determine whether Agent Zero can serve as the first runtime behind an abstraction that can later support OpenJarvis, OpenCode, Ollama, custom runtimes, and future agent frameworks without changing the user-facing product.

### Core principle

> The user owns the agent experience. The runtime is replaceable infrastructure.

---

# 2. Operating Rules

The implementation agent MUST:

1. Work from the current machine state rather than assumptions.
2. Inspect the repository/project before making architectural decisions.
3. Use official Agent Zero documentation/repository as the primary source.
4. Prefer reproducible installation methods.
5. Avoid modifying the host machine unnecessarily.
6. Prefer Docker/containerized execution where appropriate.
7. Record every significant discovery.
8. Separate facts from assumptions.
9. Do not permanently couple AgentHost to Agent Zero APIs.
10. Do not begin AgentHost implementation until the evaluation report is complete.
11. Do not silently install paid/cloud services.
12. Do not expose API keys or secrets in logs/reports.
13. Do not disable security controls merely to make Agent Zero work.
14. Preserve a clear rollback path for every host-level change.
15. Treat Windows support as a first-class requirement.

---

# 3. Current Product Direction

The target platform is a **runtime-agnostic personal AI system**.

Conceptually:

```text
                         Agent Platform
                               │
                    ┌──────────┴──────────┐
                    │                     │
              Control Plane          AgentHost
                 Laravel              Local Daemon
                    │                     │
                    └──────────┬──────────┘
                               │
                       Runtime Contract
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         Agent Zero        OpenJarvis        Future
           Adapter           Adapter         Adapters
              │                │                │
              └────────────────┼────────────────┘
                               │
                        Model Providers
```

Agent Zero is therefore a **candidate runtime**, not the platform architecture.

---

# 4. Phase A — Environment Discovery

Before installing anything, perform a complete machine assessment.

Collect:

## Operating System

- OS and edition
- OS version
- architecture
- WSL availability
- virtualization availability
- Docker availability

## Hardware

- CPU model
- CPU cores/threads
- RAM
- GPU model
- GPU VRAM
- GPU driver
- CUDA availability
- disk capacity
- available disk space

## Development Environment

Detect:

- Git
- Python
- uv
- pip
- Node.js
- npm/pnpm
- Docker
- Docker Compose
- PowerShell
- WSL
- browser installations

## AI Environment

Detect:

- Ollama
- local models
- OpenRouter configuration
- OpenAI configuration
- Anthropic configuration
- Gemini configuration
- other model providers
- existing agent runtimes

## Networking

Determine:

- internet connectivity
- localhost networking
- Docker networking
- relevant firewall restrictions
- whether outbound HTTPS works

Do NOT expose credentials while performing this inspection.

---

# 5. Phase B — Agent Zero Research

Research Agent Zero using official sources first.

Determine:

## Architecture

Identify:

- primary language
- runtime model
- process architecture
- tool architecture
- memory architecture
- browser support
- code execution
- filesystem access
- shell execution
- MCP support
- multi-agent capabilities
- persistent state
- configuration mechanism
- extension mechanism

## Installation

Document:

- recommended installation method
- Docker support
- native installation
- Windows compatibility
- Linux compatibility
- macOS compatibility
- dependency requirements
- GPU requirements
- model requirements
- configuration requirements

## Operation

Determine:

- CLI availability
- API availability
- HTTP interface
- WebSocket/streaming support
- health endpoint
- logs
- process lifecycle
- graceful shutdown
- restart behavior
- configuration reload
- headless operation

## Extensibility

Determine how Agent Zero supports:

- custom tools
- skills
- prompts
- extensions
- integrations
- MCP
- custom model providers
- custom memory
- custom agents

## Security

Evaluate:

- filesystem isolation
- shell execution risks
- browser isolation
- Docker isolation
- secret management
- permissions
- network restrictions
- arbitrary code execution
- user separation

---

# 6. Phase C — Controlled Agent Zero Installation

Install Agent Zero using the safest supported method.

Preferred order:

1. Docker/container
2. isolated environment
3. native installation

Do not pollute the host Python environment.

The installation must be reproducible.

Record:

```text
Installation Method
Agent Zero Version
Base Image / Python Version
Dependencies
Configuration Files
Volumes
Ports
Environment Variables
Startup Command
Health Check
```

Create a machine-readable installation record.

---

# 7. Phase D — Functional Smoke Test

Once Agent Zero is running, verify basic operation.

Test:

### Basic interaction

- simple question
- multi-turn conversation
- streaming response

### Reasoning

- moderately complex reasoning task
- multi-step task

### Files

- read a test file
- create a test file
- modify a test file

### Shell

- execute harmless command
- capture output
- verify error handling

### Web

- perform a simple web task if supported
- inspect browser integration

### Memory

- store a test fact
- restart runtime
- verify persistence

### Tools

- invoke a built-in tool
- determine tool discovery mechanism

### Failure

Intentionally test:

- invalid model
- unavailable tool
- failed command
- network failure
- runtime restart

Record behavior for every test.

---

# 8. Phase E — Agent Zero / AgentHost Compatibility Analysis

Determine what AgentHost would need to abstract.

Create a capability matrix:

| Capability | Agent Zero | AgentHost abstraction needed |
|---|---|---|
| Start | ? | `start()` |
| Stop | ? | `stop()` |
| Restart | ? | `restart()` |
| Health | ? | `health()` |
| Chat | ? | `execute()` |
| Streaming | ? | `stream()` |
| Models | ? | `models()` |
| Tools | ? | `tools()` |
| Skills | ? | `skills()` |
| Memory | ? | `memory()` |
| Browser | ? | capability |
| Shell | ? | capability |
| Filesystem | ? | capability |
| MCP | ? | capability |
| Configuration | ? | `configure()` |
| Logs | ? | `logs()` |
| Metrics | ? | `metrics()` |

Use `SUPPORTED`, `PARTIAL`, `UNSUPPORTED`, or `UNKNOWN`.

Do not fill gaps with assumptions.

---

# 9. Phase F — Runtime Adapter Design

Based on actual findings, define the minimum runtime contract.

Initial conceptual interface:

```text
RuntimeAdapter

discover()
install()
configure()
start()
stop()
restart()
health()
capabilities()
models()
execute()
stream()
cancel()
logs()
diagnostics()
```

Do not implement all of these automatically.

First determine which are actually required.

The Agent Zero adapter should translate between AgentHost's stable contract and Agent Zero's native interfaces.

Example:

```text
AgentHost
   │
   ▼
RuntimeAdapter
   │
   ▼
Agent Zero
```

AgentHost must never directly depend on Agent Zero internals outside the adapter.

---

# 10. Phase G — Hardware-Aware Runtime Selection

Design the future resolver.

The resolver should eventually consider:

```text
Hardware
+
OS
+
Installed Software
+
Available Runtimes
+
Available Models
+
User Requirements
+
Privacy Preferences
+
Network Availability
+
Performance Requirements
+
Installation Complexity
+
Reliability
```

Produce a deterministic first-generation scoring model.

Example:

```text
Hardware Fit          25%
Capability Fit        25%
Reliability           20%
Performance            10%
Installation Cost      10%
Privacy                10%
```

Do not use an LLM to make the bootstrap decision in v1.

The resolver should be deterministic and explainable.

Example output:

```text
Recommended Runtime

Agent Zero

Why:

✓ Supports required capabilities
✓ Compatible with detected environment
✓ Supports selected model
✓ Required tools available
✓ Installation complexity acceptable

Alternative:

Ollama
OpenJarvis

Confidence: 87%
```

---

# 11. Phase H — Suitability Scoring

Score Agent Zero against these dimensions:

| Category | Weight |
|---|---:|
| Installation simplicity | 15 |
| Windows compatibility | 15 |
| Linux compatibility | 10 |
| Runtime stability | 10 |
| Agent capabilities | 15 |
| Tool ecosystem | 10 |
| Model flexibility | 10 |
| Extensibility | 5 |
| Security/isolation | 5 |
| AgentHost integration | 5 |

Score each category from 1–10.

Calculate weighted score.

Do not inflate scores.

A serious weakness should materially affect the final recommendation.

---

# 12. Phase I — Adoption Analysis

Evaluate Agent Zero specifically against the product goal:

> A normal user should be able to install the platform and become productive within minutes without understanding agent infrastructure.

Measure:

### Setup friction

- number of installation steps
- number of decisions
- number of configuration files
- number of environment variables
- number of dependencies
- number of failure points

### Runtime friction

- startup time
- model configuration complexity
- recovery from failures
- update complexity
- logs/debugging experience

### User experience

Determine whether Agent Zero can be hidden behind AgentHost without exposing its complexity.

---

# 13. Phase J — Security Assessment

AgentHost will eventually execute powerful actions.

Therefore explicitly evaluate:

```text
Filesystem
Shell
Browser
Network
Credentials
Secrets
Processes
Docker
User permissions
Agent-to-agent communication
Tool permissions
```

Classify each as:

- Safe by default
- Requires sandbox
- Requires explicit user permission
- Dangerous
- Unknown

Design AgentHost around **least privilege**.

The default policy should favor:

```text
Read       → allowed
Write      → confirmation
Execute    → confirmation
External   → confirmation
Destructive → confirmation
```

Do not weaken security simply to improve demos.

---

# 14. Phase K — Agent Zero Suitability Report

Produce:

```text
docs/
└── agent-zero-evaluation.md
```

The report must contain:

1. Executive Summary
2. Tested Environment
3. Agent Zero Version
4. Installation Experience
5. Architecture Findings
6. Functional Test Results
7. Capability Matrix
8. Security Findings
9. Windows Findings
10. Performance Findings
11. Extensibility Findings
12. AgentHost Integration Findings
13. Weighted Score
14. Strengths
15. Weaknesses
16. Blocking Issues
17. Workarounds
18. Recommendation
19. Recommended Role
20. Next Steps

Final recommendation must be exactly one of:

```text
ADOPT
ADOPT WITH CONSTRAINTS
EXPERIMENTAL
REJECT
```

---

# 15. Phase L — AgentHost Architecture Plan

Only after completing the Agent Zero evaluation, design AgentHost.

Initial target:

```text
agent-host/
│
├── host/
│   ├── lifecycle/
│   ├── diagnostics/
│   ├── hardware/
│   ├── environment/
│   └── process/
│
├── runtime/
│   ├── contract/
│   ├── registry/
│   ├── resolver/
│   └── adapters/
│       └── agent_zero/
│
├── models/
│   ├── registry/
│   ├── discovery/
│   └── resolver/
│
├── capabilities/
│
├── tools/
│
├── skills/
│
├── security/
│   ├── permissions/
│   ├── secrets/
│   └── sandbox/
│
├── config/
│
├── api/
│
└── cli/
```

This is an architectural target, not a requirement to implement everything immediately.

---

# 16. AgentHost Initial Responsibilities

AgentHost should own:

### Machine

- hardware discovery
- environment discovery
- dependency detection
- runtime discovery

### Runtime

- installation
- lifecycle
- configuration
- health
- diagnostics

### Intelligence

- model discovery
- model compatibility
- model selection
- fallback

### Security

- permissions
- credentials
- sandboxing
- audit

### Communication

- local API
- streaming
- events
- status

AgentHost should NOT own agent-specific reasoning logic.

---

# 17. Laravel's Future Role

Laravel should remain outside the local runtime boundary initially.

Potential future architecture:

```text
                 Laravel
              Control Plane
                    │
          ┌─────────┴─────────┐
          │                   │
       Web UI              API/Auth
          │                   │
          └─────────┬─────────┘
                    │
                 AgentHost
                    │
             Runtime Adapter
                    │
              Agent Runtime
```

Laravel may eventually manage:

- users
- authentication
- devices
- agent profiles
- runtime registry
- model registry
- skills
- marketplace
- cloud sync
- remote management
- automations
- billing
- telemetry
- backups

But AgentHost must be capable of functioning independently.

---

# 18. Required Deliverables

The evaluation phase must produce:

```text
docs/
├── agent-zero-evaluation.md
├── agent-zero-installation.md
├── agent-zero-capability-matrix.md
├── agent-zero-security.md
└── agenthost-plan.md
```

Also produce:

```text
artifacts/
├── environment-report.json
├── runtime-report.json
└── capability-report.json
```

Do not commit secrets.

---

# 19. Definition of Done

This phase is complete only when:

- Agent Zero has been researched.
- Agent Zero has been installed in an isolated/reproducible manner.
- Agent Zero has been executed successfully.
- Core capabilities have been tested.
- Failure behavior has been tested.
- Windows-specific friction has been documented.
- Security implications have been documented.
- Agent Zero's actual interfaces have been inspected.
- Runtime abstraction requirements have been identified.
- Agent Zero has received a weighted suitability score.
- A clear ADOPT / ADOPT WITH CONSTRAINTS / EXPERIMENTAL / REJECT decision has been made.
- AgentHost architecture has been proposed based on evidence.
- Agent Zero-specific implementation details are isolated behind an adapter boundary.

---

# 20. Final Principle

Do not ask:

> "How do we make Agent Zero our agent?"

Ask:

> "What does a world-class AgentHost need to provide, and can Agent Zero be one runtime behind it?"

If Agent Zero is excellent, keep it.

If OpenJarvis is better for a particular machine, use OpenJarvis.

If Ollama is better for another workload, use Ollama.

If a future runtime is better, add another adapter.

The user should never have to care.

**AgentHost is the product. Runtimes are replaceable infrastructure.**