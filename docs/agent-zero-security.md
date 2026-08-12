# Agent Zero Security Assessment

Scope: Agent Zero **v2.8** as a candidate runtime behind AgentHost. Classification: **Safe by default · Requires sandbox · Requires explicit user permission · Dangerous · Unknown**.

## 1. Threat Model Context

AgentHost will eventually execute powerful actions on the user's behalf. The runtime (Agent Zero) is one part; the permission boundary AgentHost adds is the other. Findings below separate **runtime-internal** controls from **host-level** exposure.

## 2. Assessment by Surface

| Surface | Classification | Findings / Evidence |
|---|---|---|
| Filesystem | Requires sandbox | Agent filesystem is **inside the container** (`/a0/usr`). Host files are only reachable via A0 CLI Connector (explicit Read/Write grant, user-trusted) or bind mounts (explicit user action). Project isolates files, memory, secrets per project. |
| Shell | Requires sandbox | bash + code execution live inside the container (verified: `code_exe` ran Python). Privilege = container root. Projet docs: keep in Docker, do not weaken. Native (non-Docker) Windows path needs RFC. |
| Browser | Requires sandbox | Browser runs in-container; annotations/actions are agent-driven. Host browser via A0 CLI requires explicit user consent. |
| Network | Requires explicit user permission | Container can reach host services via `host.docker.internal` (verified with Ollama) and the internet for model calls. Tunnel feature (Flare Tunnel) exposes the UI publicly — project docs require credentials before tunneling. |
| Credentials | Requires explicit user permission | API keys in `usr/.env`, managed via UI; masked in settings output (`****PSWD****`, `************`). Keys never logged by us. Settings save writes to `.env`, not logs. |
| Secrets | Requires explicit user permission | Project-scoped secrets store exists; docs warn against putting credentials in prompts or public files. |
| Processes | Requires sandbox | All runtime processes inside container (supervisord-managed: searxng, tunnel, self-update, uvicorn — observed in `ps`). |
| Docker | Requires explicit user permission | Requires Docker Desktop/WSL2 (privileged host daemon). Image is a full Linux desktop; keep on trusted machine only. |
| User permissions | Requires explicit user permission | Web UI login/password optional (default: OPEN). **Critical finding:** with empty UI credentials, the API token is derivable (`sha256(runtime_id::)[:16]`) — anyone with LAN access can call the API. UI credentials MUST be set before any non-loopback exposure. |
| Agent-to-agent (A2A/MCP) | Requires explicit user permission | Both opt-in (`mcp_server_enabled`, `a2a_server_enabled`), token-authed (`t-{TOKEN}` URLs, same token as API). | 
| Tool permissions | Requires explicit user permission | No per-tool permission prompts inside runtime; tools run as container root. Permission model must come from AgentHost layer. |
| Update/self-update | Safe by default (with caution) | Self-Update executes code from project pipelines; internal backups managed. Keep on trusted network. |

## 3. Runtime-internal protections (documented + corroborated)

- Whole runtime isolated in Docker (project's stated safety model: "Keep it running inside Docker").
- Settings UI masks secrets; `.env` is source of truth for keys.
- API key required for external endpoints (verified 401 without key).
- Unusable-response guard prevents runaway LLM cost loops (verified).
- Time Travel snapshots give recoverable agent-workspace history (not a backup).

## 4. Controls AgentHost must add (least privilege)

| Control | Design |
|---|---|
| Host filesystem | Default: no host mounts. Explicit, scoped grants only (A0 CLI Connect or bind-mount wizard). |
| Actions | Policy: Read → allowed; Write/Execute/External/Destructive → confirmation (interactive or allowlist). AgentHost enforces at the API-call boundary (context: message routing), not inside A0. |
| Network | Outbound LLM calls whitelisted by provider; tunnel creation requires user consent + credentials already set. |
| Secrets | AgentHost vault (OS keychain) at rest; inject only at install/configure time; never echo. |
| Audit | Audit log of every AgentHost→runtime call: who/what/result. A0 journal (`api_log_get`) provides traceability inside runtime. |
| Token handling | AgentHost auto-generates random UI credentials at install (drives a stored token); stores token in vault; rotates on demand. |

## 5. Top risks

1. **Open Web UI by default** (no credentials) + derivable API token → any LAN client can drive the agent. HIGH.
2. **Container-root agent** with full tool surface (browser, shell, file) → sandbox is the isolation; container escape would be very bad. MEDIUM (standard Docker exposure).
3. **Crawling/leaking prompts**: tool list + system prompt are transmitted to LLM provider (cloud plan) — provider sees user data if cloud models used. Privacy consideration for users. MEDIUM (configurable provider choice).
4. **Self-update** executes remote code path. MEDIUM.
5. **Shipped third-party services inside image** (searxng instance observed) — default search infra running in container. LOW.

## 6. Verdict

Agent Zero is **not safe by default against a malicious prompt**, but is **reasonably sandboxed by design** (Docker-only). AgentHost must treat it as a semi-trusted worker: default-open-NO, credentials YES, host access NO by default, all actions audited.