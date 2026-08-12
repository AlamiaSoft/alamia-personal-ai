# AgentHost Future Phase Roadmap

## Phase 2: Controlled Empirical Capability Probing System

### Overview
The AgentHost v0.1 core resolver is now frozen and production-ready with strict evidence-driven constraints:
- **UNKNOWN capability stays UNKNOWN** (`confidence = 0.0`).
- **Structural fit does not mutate capability evidence**.
- **Verified capability outranks an unverified structural candidate**.
- **Discovery order cannot influence the winner**.
- **Ties are deterministic**.
- **Runtime requirements are correctly separated from model capabilities**.

The next phase will build the missing bridge between **Structural Suitability** and **Empirical Capability Verification**.

---

### Key Requirements & Evidence Record Schema

When models are probed, the system will record controlled empirical evidence with the following schema:

```json
{
  "model_id": "ollama/deepseek-r1:14b",
  "digest": "sha256:7e9972...",
  "task_category": "coding",
  "probe_version": "v1.2.0",
  "test_result": {
    "syntax_validity": 1.0,
    "pass_at_1": 0.88,
    "execution_time_ms": 1420
  },
  "capability_score": 0.88,
  "timestamp": "2026-08-12T20:17:49Z",
  "confidence": 0.91
}
```

---

### Resolver Evolution

The empirical probing suite will allow AgentHost recommendations to dynamically transition from:

```text
BEST STRUCTURAL CANDIDATE
capability UNKNOWN
```

to:

```text
BEST VERIFIED CANDIDATE
coding confidence: 0.91
tool-use confidence: 0.84
```

This transforms AgentHost into a genuinely differentiated, empirical execution profile resolver.
