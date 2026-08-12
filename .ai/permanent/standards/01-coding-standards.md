# AgentHost Coding Standards & Testing Strategy

## 1. Code Standards & Architecture Guidelines

### 1.1 Language & Framework Conventions
- **TypeScript / Python**: Explicit typing required across all schemas, interfaces, and function parameters. No `any` types allowed.
- **Immutability & Pure Functions**: Business logic, resolution scoring, task requirement parsing, and tool filtering must be implemented as pure, side-effect-free functions.
- **Interface Segregation**: Modules interact exclusively through clear contracts (e.g., `RuntimeAdapter`, `ModelRegistry`, `TaskAnalyzer`).

### 1.2 Error Handling & Taxonomy
Never swallow exceptions or mask errors with silent fallbacks. All errors must be classified using the standard AgentHost error taxonomy:

```text
DISCOVERY_ERROR        # Host hardware/environment discovery failed
CONFIGURATION_ERROR    # Invalid execution profile or adapter configuration
PREFLIGHT_FAILED       # Preflight validation failed (contains explicit reasons)
RUNTIME_UNAVAILABLE    # Candidate runtime container/process unready or unresponsive
MODEL_UNAVAILABLE      # Model not found or quota/VRAM exhausted
CAPABILITY_MISMATCH    # Task requirement exceeds available capability
QUOTA_EXCEEDED         # Token or rate limit exceeded
RUNTIME_ERROR          # Error returned from runtime execution (mapped)
```

---

## 2. Security Standards

1. **Vault Storage**: Credentials (API tokens, RPC keys) must be stored in secure local configuration vaults, never hardcoded or stored in plain text repository files.
2. **Log Sanitization**: Scrub all credentials, tokens, and authorization headers (`X-API-KEY`, bearer tokens) before emitting logs or SSE events.
3. **Network Isolation**: Native HTTP daemon sockets bind strictly to `127.0.0.1`.

---

## 3. Testing Strategy

### 3.1 Unit & Schema Tests
- Strict validation of `ModelProfile`, `HardwareProfile`, `ExecutionProfile`, and `TaskRequirements` schemas.
- Mathematical verification of evidence confidence scoring:
  $$\text{effective\_capability} = \text{capability\_score} \times \text{evidence\_confidence}$$

### 3.2 Deterministic Resolver Tests
- Benchmark the resolver using fixed hardware profiles (e.g., GTX 1080 Ti 11GB VRAM, 32GB RAM) and verified task requirement sets.
- Ensure resolver outputs reproducible, ranked execution profiles with explicit explainability lists.

### 3.3 Contract Tests (`RuntimeAdapter`)
- Test `Agent Zero Adapter` mock and live Docker interactions against the standard `RuntimeAdapter` interface contract (`start`, `stop`, `health`, `execute`, `logs`).

### 3.4 Fixture Preservation
- Use completed empirical evaluation reports (`artifacts/*.json`) as fixed test fixtures for unit and integration suites.
