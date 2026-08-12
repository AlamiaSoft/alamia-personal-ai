# Agent Zero Capability Matrix (v2.8)

Legend: **SUPPORTED** = verified in this evaluation · **PARTIAL** = exists/usable with constraints · **UNSUPPORTED** = absent · **UNKNOWN** = not verifiable in this evaluation

Machine-readable version: `artifacts/capability-report.json`

| Capability | Agent Zero (v2.8) | AgentHost abstraction | Rating |
|---|---|---|---|
| Start | `docker run` / A0 installer | `start()` | SUPPORTED |
| Stop | `docker stop` | `stop()` | SUPPORTED |
| Restart | `docker restart` (persists `/a0/usr`) | `restart()` | SUPPORTED |
| Health | HTTP 200 on `/`; readiness in logs; no dedicated `/health` | `health()` | PARTIAL |
| Chat | `POST /api/api_message` (X-API-KEY) | `execute()` | SUPPORTED |
| Streaming | WebSocket socket.io v4 (verified handshake); REST returns final JSON only | `stream()` | PARTIAL |
| Models | Provider list (openrouter, anthropic, openai, gemini, groq, ollama, lm_studio, llama_cpp, omlx, vllm, a0_venice) + preset mechanism | `models()` | SUPPORTED |
| Tools | Auto-injected tool list per turn; transparent journal (response, code_exe, file, copy, bash, browser…) | `tools()` | SUPPORTED |
| Skills | Load-on-demand / pinned per chat; `/a0/usr/skills` | `skills()` | SUPPORTED |
| Memory | faiss recall + util-LLM extraction every turn; project-scoped subdirs | `memory()` | PARTIAL¹ |
| Browser | Built-in DOM-annotation browser (GUI canvas); host browser via A0 CLI | capability | SUPPORTED² |
| Shell | bash + code_execution inside container; RFC for native Windows hosts | capability | SUPPORTED |
| Filesystem | Workdir `/a0/usr/workdir`; `api_files_get` (base64) | capability | SUPPORTED |
| MCP | Client (`mcp_servers` config) + Server (SSE `/mcp/sse`, streamable HTTP `/mcp/http/`) | capability | SUPPORTED |
| A2A | FastA2A server at `/a2a/t-{TOKEN}` (opt-in) | capability | SUPPORTED |
| Configuration | `usr/settings.json` + `usr/.env` + plugin configs + legacy `A0_SET_*` | `configure()` | SUPPORTED |
| Logs | `GET/POST /api/api_log_get` (per-context journal) + `docker logs` | `logs()` | SUPPORTED |
| Metrics | None observed; uvicorn access-log toggle only | `metrics()` | UNKNOWN |
| Cancel | `api_terminate_chat` (destructive) verified; in-flight cancel via WS events | `cancel()` | PARTIAL |
| Diagnostics/Updates | Self-Update UI; `update_check_enabled` | `diagnostics()` | PARTIAL |

¹ Memory recall executes every turn (journal-verified) but is tied to utility-model quality; store+restart persistence not LLM-verifiable with the models available on this machine.

² Browser surface ships in the image and is documented; not driven in this evaluation (GUI + stronger model required).

## Model Findings (drive capability constraints)

- **Local Ollama (host GPU):** `qwen2.5-coder:7b/14b` handle simple chat and single `code_exe` calls but **fail the v2.8 unified-turn tool-JSON protocol on multi-tool flows** — the 5-consecutive-unusable-response guard trips. Verified repeatedly. Not viable as the agent brain on this hardware.
- **Groq free tier:** tool protocol works (file created with `llama-3.3-70b-versatile`) but free TPM caps (6k–12k) are **below A0's ~11.3k-token minimum request** (prompt + tool definitions), so every turn hits the rate limiter.
- **OpenRouter key on host:** valid but **zero credits** (HTTP 402).
- => On this machine, a viable agent requires either a smaller tool surface, a paid strong cloud model, or a much stronger local model than 11 GB VRAM can comfortably run.

## Integration Surface (for AgentHost adapter)

| Area | Fact |
|---|---|
| Lifecycle | Docker API (start/stop/restart/logs), name-pinned containers |
| Chat | REST `POST /api/api_message` (context_id, message, attachments, project_name, lifetime_hours) |
| Logs | `api_log_get` journal per context |
| Files | `api_files_get` (base64), uploads via attachments |
| Config | file-based presets + `usr/.env` secrets + legacy env defaults |
| Streaming | socket.io WS (UI); REST is request/response |
| Auth | `X-API-KEY` token derived from runtime_id + credentials |
| Remote agent interop | MCP server/client + A2A (FastA2A) — AgentHost can integrate as MCP client or A2A peer |