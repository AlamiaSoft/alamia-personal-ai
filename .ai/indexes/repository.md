# Repository Code & Concept Index

This index maps high-level architectural concepts to target codebase paths, specifications, and records.

## Concept Mapping Matrix

| Concept | Target Location / Spec | Description & Intent |
|---|---|---|
| **System Architecture** | [.ai/permanent/architecture/01-system-architecture.md](file:///f:/Playgrounds/alamia-personal-ai/.ai/permanent/architecture/01-system-architecture.md) | High-level design, topological flow, core abstractions |
| **Runtime Adapter Contract** | `agenthost/execution/contract/` | Standard interface (`RuntimeAdapter`) for runtime lifecycle & messaging |
| **Agent Zero Adapter** | `agenthost/execution/adapters/agent_zero/` | Containerized Agent Zero v2.8 adapter |
| **Resource Discovery** | `agenthost/discovery/` | Hardware, OS, runtime, and model environment scanners |
| **Model Registry & Profiles** | `agenthost/knowledge/model-profiles/` | Model profile dataset with evidence confidence scoring |
| **Task Analyzer** | `agenthost/resolution/task-analyzer/` | Deterministic classifier for task requirement extraction |
| **Tool Selector** | `agenthost/resolution/tool-selector/` | Capability-driven tool injection engine |
| **Execution Profile Resolver** | `agenthost/resolution/execution-profile-resolver/` | Composite resolver scoring runtime/model/hardware fit |
| **Preflight Validation** | `agenthost/resolution/preflight/` | Profile & task preflight validators |
| **Security & Vault** | `agenthost/security/` | Credentials vault, loopback binding, audit logger |
| **CLI & User Interface** | `agenthost/interface/cli/` | Commands: `scan`, `doctor`, `setup`, `run` |

---

## Architectural Decision Records
- [ADR 0001: Adopt Agent Zero v2.8 as First Candidate Runtime](file:///f:/Playgrounds/alamia-personal-ai/.ai/permanent/adr/0001-adopt-agent-zero-runtime.md)
