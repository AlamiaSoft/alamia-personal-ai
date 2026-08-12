# ADR 0001: Adopt Agent Zero v2.8 as First Candidate Runtime

## Context
AgentHost requires an initial agent runtime to evaluate runtime contract abstractions, host integration, and model resolution. Agent Zero v2.8 was thoroughly evaluated across installation, performance, memory, security, and tool calling capabilities.

## Decision
Adopt Agent Zero v2.8 as the **first candidate runtime** under the status **ADOPT WITH CONSTRAINTS**.

## Constraints & Rules
1. **Adapter Isolation**: Agent Zero must be accessed exclusively through the `RuntimeAdapter` interface. AgentHost code outside the adapter boundary must never import or depend directly on Agent Zero internals.
2. **Container Execution**: Agent Zero must run containerized in Docker to ensure environment reproducibility and filesystem isolation.
3. **API Mediation**: Communication is conducted strictly via HTTP REST and Socket.io WebSocket APIs (`/api/api_message`, `/api/api_log_get`). Direct shell/script invocation on host python is prohibited.
4. **Prompt Optimization**: AgentHost will control tool injection dynamically to reduce default ~11.3k prompt baseline token overhead.
