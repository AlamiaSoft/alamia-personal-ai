# Agent Zero Installation Report

**Date:** 2026-08-12  
**Method:** Docker container (official image), controlled evaluation instance  
**Environment:** Windows 11 Home (26200), Docker Desktop + WSL2 backend

## 1. Installation Record

| Item | Value |
|---|---|
| Installation Method | Docker (official image pulled and run manually via CLI) |
| Agent Zero Version | v2.8 (commit `5ff106a2`, 2026-08-01) |
| Image | `agent0ai/agent-zero:latest` (12.4 GB, digest `sha256:8c5eff81...`) |
| Container | `a0-eval` |
| Ports | Host `5080` → container `80` (HTTP/WebSocket, uvicorn) |
| Volume | `a0_eval_usr` → `/a0/usr` (all user data; never mount whole `/a0`) |
| Container Python | App venv `/opt/venv-a0` (Python 3.12 app / 3.13 system) |
| Startup Command | `docker run -d --name a0-eval -p 5080:80 -v a0_eval_usr:/a0/usr agent0ai/agent-zero:latest` |
| Health Check | `GET http://localhost:5080` returns 200; logs contain `Agent Zero is running.` |
| Startup Time | Web UI served ~20 s after container start |
| Restart Behavior | `docker restart` → UI up in ~20–25 s; volume data persists |

## 2. Configuring Models (v2.8 — important)

**Legacy mechanism is `A0_SET_*` env vars** (e.g. `A0_SET_chat_model_provider=ollama`). These still exist but **v2.8 model configuration is file-based** via the `_model_config` plugin:

- Presets: `/a0/usr/plugins/_model_config/presets.yaml`
- Active selection: `/a0/usr/plugins/_model_config/config.json` → `{"model_preset": "<name>"}`

A model preset contains `chat`, `utility`, and `embedding` slots (provider, name, api_base, ctx_length, kwargs).

For local Ollama on the host use `api_base: http://host.docker.internal:11434` (verified working).

**Requirements (verified):**

- `chat` LLM: mandatory. v2.8's `unified_turn` protocol requires strict tool-call JSON output. Local 7B/14B models failed on multi-tool flows (5-consecutive-unusable-response guard). Strong cloud models are the intended profile (shipped presets use gpt-5.6-class / gemini-flash-lite).
- `utility` LLM: used on **every turn** for memory extraction/summarization. Project docs: models ≤ 4B are unreliable.
- `embedding`: optional; default local sentence-transformers (CPU).

## 3. Onboarding / First Run

1. Open `http://localhost:5080`.
2. Complete onboarding (choose Cloud / AI account / Local).
3. Save credentials in Settings → Authentication (see security note below).
4. Select model preset.

## 4. API Access (AgentHost-relevant)

- Token: `X-API-KEY` header. Token = `base64url(sha256(runtime_id:auth_login:auth_password))[:16]`.
- **Security note:** with empty UI credentials the token is derivable from public inputs — set credentials before any non-loopback exposure.
- Endpoints verified: `POST /api/api_message`, `GET|POST /api/api_log_get`, `POST /api/api_reset_chat`, `POST /api/api_terminate_chat`, `POST /api/api_files_get`, `GET /api/settings_get` (browser session), WebSocket `socket.io` (streaming channel).
- Without `X-API-KEY` → `401`.

## 5. Update Path

Self-Update via Settings UI. v1 → v2 major jumps require backup/restore + new image (documented by project). Backups exist internally; user data lives in `/a0/usr`.

## 6. Rollback (this evaluation)

```text
docker rm -f a0-eval
docker volume rm a0_eval_usr
docker image rm agent0ai/agent-zero
```

Docker Desktop was started (was installed but stopped). Side effect: starting it auto-started other pre-existing containers on the machine.

## 7. Windows-Specific Findings

- REQUIRES Docker Desktop with WSL2 — currently the only sanctioned Windows path. Native (non-Docker) install exists but needs RFC for shell execution.
- Full containerized Linux desktop + LibreOffice + browser run inside the image; no host install required.
- Host services (Ollama) reachable via `host.docker.internal` (verified).
- Everything else (A0 Install PowerShell script, A0 Launcher, A0 CLI Connector) is officially supported on Windows.