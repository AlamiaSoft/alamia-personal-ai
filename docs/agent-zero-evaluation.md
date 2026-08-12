# Agent Zero Evaluation Report (AgentHost Phase K)

**Candidate:** Agent Zero **v2.8** (commit `5ff106a2`, 2026-08-01) as first runtime behind AgentHost  
**Date:** 2026-08-12 · **Machine:** Windows 11 Home, i5-12400F, 32 GB RAM, GTX 1080 Ti 11 GB  
**Method:** Official docs + source inspection + controlled Docker install + functional smoke tests

---

## 1. Executive Summary

Agent Zero is a mature, actively developed (v2.8, 18k+ stars) Docker-centric agent framework with one of the **strongest integration surfaces we evaluated**: REST API, WebSocket streaming, MCP server **and** client, FastA2A, transparent per-turn tool journal, project isolation, skills, plugins, memory, and a full Linux desktop/browser inside its container. Windows support is first-class via Docker Desktop/WSL2 and works out of the box on this machine.

Two material constraints were verified empirically:

1. **Model requirement is steep.** v2.8's `unified_turn` protocol demands strict tool-call JSON output. Local 7–14B models (host GPU, 11 GB VRAM) **fail reliably on multi-tool flows** (5-strike unusable-response guard). The shipped presets target strong paid cloud models; the project itself warns small models fail utility/memory tasks.
2. **Free-tier model access isn't sufficient on this machine.** Groq free TPM caps (6–12k) sit below A0's ~11.3k-token minimum request; the OpenRouter key on this machine has zero credits.

**Recommendation: ADOPT WITH CONSTRAINTS** as the first runtime behind AgentHost — subject to a paid strong model (or sufficiently strong local model ≥ ~30B class), Docker Desktop as a hard dependency, and AgentHost enforcing credential/permission defaults (see §17).

## 2. Tested Environment

- Windows 11 Home build 26200 (x64), Intel i5-12400F (6c/12t), 32 GB RAM, GTX 1080 Ti (11 GB, driver 582.66)
- Docker Desktop 29.6.1 + WSL2 (Ubuntu 24.04 backend), Docker Compose v5.1.4
- Ollama 0.32.9 on host (qwen2.5-coder 7b/14b/1.5b, qwen2.5 7b, qwen3.5 4b, deepseek-r1 14b, bge-m3)
- Host API keys: OpenRouter (0 credits), Groq (free tier)
- Full report: `artifacts/environment-report.json`

## 3. Agent Zero Version

v2.8 tagged + commit `5ff106a2` (2026-08-01). Official image `agent0ai/agent-zero:latest`, digest `sha256:8c5eff81a46f...`, 12.4 GB.

## 4. Installation Experience

Reproducible Docker install; UI up in ~20 s. Configuration has **two worlds**: legacy `A0_SET_*` env vars (still honored) and the v2 file-based `_model_config` plugin (presets.yaml + config.json) which is authoritative for models. Docs lag the code here — the env-var path we started with was ignored in favor of presets. Myth-busted quietly; nothing broke. Findings: `docs/agent-zero-installation.md`, `artifacts/runtime-report.json`.

## 5. Architecture Findings

- Pure Python (FastAPI/uvicorn + Flask-style handler classes + Alpine.js WebUI; socket.io WS), runs under supervisord in a full Linux desktop container (XFCE/LibreOffice/searxng).
- **Tool architecture:** tools injected per-turn into the model prompt; execution transparently journaled. Verified: `response`, `code_exe` (Python), file tools, bash, browser, copy.
- **Memory:** faiss recall + util-LLM extraction on every turn (observed in journal); project-scoped memory subdirs; Time Travel snapshots for workspace.
- **Multi-agent:** superior/subordinate agents (subagent context isolation).
- **Extension:** plugin hub (100+ plugins), custom tools/prompts/skills, MCP client+server, A2A.
- **State/config:** `usr/settings.json`, `usr/.env` (secrets), plugin configs; project-scoped configs.
- **No metrics endpoint;** `/health` not exposed (HTTP 200 on `/` only).

## 6. Functional Test Results (evidence in `artifacts/capability-report.json`)

| Test | Result |
|---|---|
| Basic interaction | PASS — REST `api_message` → "READY" |
| Multi-turn | PASS — 17×23=391, then +5=396, same context |
| Reasoning (multi-step) | PARTIAL — arithmetic executed via `code_exe` tool (journal); verbose multi-step prompts trip local-model protocol failures |
| Files create/read | PASS — created `workdir/test-note.txt`; read via `api_files_get` (base64) |
| Shell | PARTIAL — `code_exe` verified; interactive bash turn unverifiable with free models |
| Web/browser | UNVERIFIED (surface present; needs GUI + strong model) |
| Memory store+restart | PARTIAL — recall engaged every turn; store/recall across restart not LLM-verifiable here |
| Tool discovery | PASS — tools injected per turn; journal exposes executed tool types |
| Streaming | PARTIAL — socket.io WS handshake verified; REST returns final JSON only |
| Failure: invalid model | PASS — structured 500 `model 'does-not-exist-xyz' not found` |
| Failure: missing key | PASS — 401 |
| Failure: invalid context | PASS — `Context not found` |
| Failure: unusable output | PASS — 5-strike guard returns clean error (observed repeatedly with 14B local) |
| Failure: provider limits | PASS — rate-limit errors surfaced as structured API errors |
| reset / terminate chat | PASS — journal 22→1; context deleted; both confirmed |

## 7. Capability Matrix

Full matrix in `docs/agent-zero-capability-matrix.md` (SUPPORTED: start/stop/restart/chat/models/tools/skills/files/shell/browser/MCP/A2A/config/logs; PARTIAL: health/streaming/memory/cancel/metrics-none).

## 8. Security Findings

`docs/agent-zero-security.md`. Headline: **open Web UI by default** — with no credentials the API token is derivable from public inputs, so any LAN client could drive the agent; credentials are mandatory before exposure. Runtime is containerized (good default); per-action permission prompts are AgentHost's job, not A0's.

## 9. Windows Findings

- Requires Docker Desktop + WSL2 — the only sanctioned install path (native exists; needs RFC for shell). Works cleanly on Windows 11 Home.
- Host Ollama reachable via `host.docker.internal:11434` (verified).
- A0 Launcher/Installer/CLI all first-class on Windows.
- Container desktop/browser mean no host GUI deps.

## 10. Performance Findings

- Startup → ready ~20–25 s; restart ~20–25 s (data persisted).
- Simple local-14B turn: measured 9.9 s (2 tokens, GPU) to ~1–3 min full turns.
- Tool execution costs multiple LLM turns (each turn resends full tool definitions — this is why Groq free TPM is insufficient).
- Memory extraction runs per turn (utility-LLM cost multiplies with chat turns).

## 11. Extensibility Findings

Documented+in-repo: plugins (100+ hub), custom tools under `tools/` or plugin folders, skills, custom prompts per agent profile, project-scoped config, MCP client/server, A2A, provider metadata files for custom providers. Verified via settings/plugin source (`helpers/api.py` route dispatch allows plugin API endpoints; `_model_config` plugin governs models).

## 12. AgentHost Integration Findings

Everything AgentHost needs exists on the **outside** of the container:
- Lifecycle: Docker API; name-pinned containers; named volume.
- Chat: REST `api_message` (context_id, attachments, project_name, lifetime).
- Logs/telemetry: `api_log_get` per-context journal; `docker logs`.
- Files: `api_files_get` (base64), attachments.
- Streaming: socket.io WS for UI-grade streaming; REST remains request/response.
- Config: file-based presets + `.env` secrets; restart required for model changes (verified).
- Auth: `X-API-KEY` derived token; AgentHost can generate and hold the token (set random UI credentials at install).
- Interop: MCP server/client + FastA2A — AgentHost could connect as MCP client or A2A peer instead of REST if desired.
- **No versioned SDK** — the API surface is HTTP-first and stable at the documented endpoints.

## 13. Weighted Score (Phase H)

| Category | Weight | Score (1–10) | Weighted |
|---|---|---|---:|
| Installation simplicity | 15 | 8 | 1.20 |
| Windows compatibility | 15 | 9 | 1.35 |
| Linux compatibility | 10 | 10 | 1.00 |
| Runtime stability | 10 | 8 | 0.80 |
| Agent capabilities | 15 | 9 | 1.35 |
| Tool ecosystem | 10 | 9 | 0.90 |
| Model flexibility | 10 | 8 | 0.80 |
| Extensibility | 5 | 9 | 0.45 |
| Security/isolation | 5 | 6 | 0.30 |
| AgentHost integration | 5 | 9 | 0.45 |
| **Total** | **100** | | **8.60 / 10** |

Scoring notes: installation −1 for the doc/config drift and Docker-only runtime; runtime stability −2 for the strict-model protocol failure mode (not a crash, but a capability cliff for modest hardware); model flexibility −2 because v2.8's protocol effectively demands strong models; security −4 for default-open credentials posture.

## 14. Strengths

- Complete, transparent agent runtime (tools, memory, browser, desktop, multi-agent) in one image.
- Excellent external surface: REST + WS + MCP + A2A + journal.
- Windows first-class via Docker; clean local-model serving story (`host.docker.internal`).
- Ergonomic failure paths (structured JSON errors, 5-strike cost guard, settings refresh, Self-Update).
- Open source, active, well documented; plugin culture.

## 15. Weaknesses

- **High model bar**: unusable-response cliff with ≤14B local models; docs warn small utility models fail memory tasks.
- **Config v1/v2 drift** (env vars vs preset files) — integration must target presets/files and verify version first.
- **No metrics endpoint**, health is implicit, streaming not on REST.
- **Open-by-default credentials** + derivable token.
- Docker Desktop hard dependency on Windows; 12.4 GB image, broad attack surface inside container (XFCE, searxng, tunnel, self-update).

## 16. Blocking Issues

1. (Blocked on this machine) No usable-paid cloud model; local models ≤14B cannot drive multi-tool agent flows. Must be resolved per-install (user supplies provider or qualifies hardware for a ≥30B-class local model).
2. None architectural: no blocker to AgentHost integration itself.

## 17. Workarounds

- Keep a **fast tier + strong tier**: simple chat on local GPU; agent-workload chats routed to a strong provider.
- If used with local models only, constrain prompts to single-tool tasks (verified working) and raise `max_consecutive_unusable_responses` deliberately.
- AgentHost sets credentials + stores token in its vault immediately after install; never exposes port 5080 beyond loopback before that.

## 18. Recommendation

**ADOPT WITH CONSTRAINTS**

- Adopt as the first runtime behind AgentHost (Docker-based lifecycle, REST+WS API, MCP/A2A options).
- Constraints: (a) require a qualified model plan (strong cloud provider or ≥30B-class local on adequate VRAM); (b) require Docker Desktop/WSL2 on Windows; (c) AgentHost must enforce credentials/token + local-only binding + action confirmation at its own boundary; (d) treat preset-file config as the integration contract, not env vars.

## 19. Recommended Role

Agent Zero = the **general-purpose worker runtime** (browser-desktop-files-shell agent) behind AgentHost — the "do real work on my machine" tier. Ollama serves as the **model-provider runtime** (already on host). OpenJarvis/code-oriented runtimes remain future adapter candidates for lightweight/terminal workloads.

## 20. Next Steps

1. (User) Provide/qualify a strong model path (paid provider key with credits, or enable a >30B local model) → rerun blocked smoke tests (bash, web, memory persistence).
2. Proceed to Phase L: AgentHost architecture plan (`docs/agenthost-plan.md`).
3. Build AgentHost `runtime/adapters/agent_zero` against the documented adapter contract (REST+WS+Docker), keeping the runtime-agnostic boundary.
4. Continuously re-verify against v2.8+ (fetch upstream notes; pin image digest in production).

---

> **Final principle:** AgentHost is the product. Runtimes are replaceable infrastructure. Agent Zero qualifies as the first replaceable runtime, not the platform.