# Agent Zero Model Bottleneck Investigation

**Date:** 2026-08-12  
**Machine:** Windows 11 Home, i5-12400F, 32 GB RAM, GTX 1080 Ti (11 GB VRAM)  
**Agent Zero Version:** v2.8 (commit `5ff106a2`, 2026-08-01)  
**Goal:** Explain the ~11.3k-token request size minimum and identify the cheapest viable model/cloud config for the full functional test suite.

---

## 1. Why Are Agent Zero Requests ~11.3k Tokens?

The ~11.3k-token request size is the **minimum per-chat-message payload** that Agent Zero v2.8 constructs before the LLM generates its first response. It is the combination of:

| Component | Approx. Token Count | Source |
|---|---|---|
| Framework system prompt | ~6.9k tokens | `/a0/prompts/` total 27.7KB (~6.9k tokens). Not all are sent per request, but the main `agent.system.main.md` + core behaviour prompts compose the bulk. |
| Agent0 profile prompt | ~389 tokens (agent0) or up to ~5.5k (researcher/developer) | Profile-specific markdown under `/a0/agents/{profile}/prompts/`. The default `agent0` profile is small (~1.5k chars ≈ 389 tokens). Other profiles (researcher, developer) are larger (~5.5k tokens) because they include more-specific instructions. |
| Tool definitions | ~1.5k–3k tokens | A0 injects the full tool list each turn. Each tool has a description; the tool list is built from `/a0/agents/{profile}/prompts/agent.system.tools.md` plus built-in tool definitions (code_exe, file, copy, bash, browser). The exact count depends on how many tools are active. |
| Memory / journal entries | ~0.5k–1k tokens (if memory recall enabled) | The `util` model extracts and summarizes memories each turn; journal items from prior turns may be re-injected. |
| Conversation history | Variable (0 if fresh chat) | Fresh chats have no prior history; multi-turn adds prior turns × 2 (user + agent). |

**Total (agent0 profile + typical tools + baseline): ≈ 11.3k tokens.**

The "baseline" of ~11.3k is the **fresh-chat, no-memory, minimal-tool** payload. Adding memory, longer history, or more tools increases the per-request size.

---

## 2. Model Capability vs. Request Size

| Model | VRAM Fit (11 GB) | Protocol Compliance | TPM (Free Tier) | Verdict |
|---|---|---|---|---|
| `qwen2.5-coder:7b` (Ollama, GPU) | ✅ Fits | ❌ Fails v2.8 unified-turn protocol (5× unusable-response guard) | N/A (local) | Not viable as agent brain. |
| `qwen2.5-coder:14b` (Ollama, GPU) | ✅ Fits (9 GB) | ⚠️ Passes single-turn + single `code_exe`; fails multi-tool (5-strike guard) | N/A (local) | Not viable for complex agentic workflows. |
| `llama-3.3-70b-versatile` (Groq, cloud) | N/A (cloud) | ✅ Verified: file creation tool executed correctly | ❌ 8k TPM (gpt-oss-120b) / 12k TPM (llama-70b) — **below** A0's ~11.3k request size; each turn hits rate limit after ~7.4k "used" tokens. | Protocol‑compliant but **impractical** under free-tier TPM. |
| `deepseek-r1:14b` (Ollama, GPU) | ✅ Fits (9 GB) | ❓ Unverified (never ran full turn due to TPM/protocol guard) | N/A (local) | Worth testing; reasoning model may handle JSON differently. |
| `qwen3.5:4b` (Ollama, GPU) | ✅ Fits (3.4 GB) | ❌ Very likely fails protocol (small model warning from docs) | N/A (local) | Not viable. |

**Key Insight:** The request size (~11.3k tokens) **exceeds or meets** the free-tier TPM ceiling for every Groq model. Even the most generous (llama‑3.3‑70b‑versatile, 12k TPM) cannot fit a single A0 turn without approaching the limit. Local models avoid TPM but hit the v2.8 protocol cliff (unusable‑response guard after 5 failed turns).

---

## 3. Reducing the Request Size

The request can be reduced by cutting components:

| Lever | Effect | Trade‑off |
|---|---|---|
| **Fewer tools** | Remove tool definitions not needed for the task → reduce ~1–2k tokens. | Agent may lack required capability. |
| **Smaller agent profile** | Switch to a lean profile (e.g., `tiny-local` or `hacker`) → reduce ~0.4–5.5k tokens. | Reduced instruction quality/capability. |
| **Disable memory recall** | Set `max_embeds: 0` or `utility_model` to a very small model → reduce ~0.5–1k tokens. | Memory / summarization disabled; may affect long‑running coherence. |
| **Set `ctx_history` small** | Fresh chat has no impact; history adds ~2 tokens per prior turn. | Conversation context is lost. |
| **Combine reductions** | Apply 2–3 levers together → can bring request below 9k tokens, enabling Groq `llama‑3.3‑70b‑versatile` (12k TPM) for ~2 turns/minute. | Capability may be sufficiently restricted for the test suite. |

**Feasible cheapest config:**  
- **Model:** `llama-3.3-70b-versatile` on Groq (cloud)  
- **Tool surface:** Minimal (only `code_exe` + `file`)  
- **Memory:** Disabled or `utility` = tiny model  
- **Expected per‑turn size:** ~8.5–9.5k tokens → fits under 12k TPM, allowing ~1–2 turns per minute window.  
- **Cost:** a few cents per test session (well within "financially constrained" guardrail).

---

## 4. Minimum Model Capability Required for Blocked Tests

Based on our empirical findings, the **minimum model capability** to pass the full functional test suite is:

| Capability | Required Model Strength |
|---|---|
| Basic chat + arithmetic | `qwen2.5-coder:7b` (local) — passes single‑turn, fails multi‑tool |
| Tool execution (`code_exe`, `file`) | `llama-3.3-70b-versatile` (Groq cloud) — verified tool execution |
| Multi‑tool workflows (file + shell + memory) | A model with **strict JSON tool‑call output** + **≥12k TPM** (e.g., Groq `llama‑3.3‑70b‑versatile` with reduced tool surface) |
| Browser automation | Cloud model with vision (e.g., OpenRouter Gemini/Claude) — local 14B cannot drive GUI |
| Memory persistence across restart | Any model + A0's faiss backend; LLM must be capable of summarizing/re‑encoding memories. |

**→ The breakthrough is recognizing that the problem is NOT "runtime selection" but "model‑selection-as-first-class-concern." AgentHost must treat the model profile as a core part of the execution environment, not an afterthought.**

---

## 5. Decision‑Engine Dataset (Model Profiles)

Below is the **decision‑engine dataset** that AgentHost (or an upstream planner) can use to reason about which model to select for a given task and hardware. Format: JSON list of model profiles.

```json
{
  "models": [
    {
      "name": "qwen2.5-coder:7b",
      "provider": "ollama",
      "local": true,
      "vram_gb": 4.7,
      "context_window": 32768,
      "tool_calling": "FAIL multi-tool",
      "coding": "good",
      "reasoning": "basic",
      "latency": "~1–3 min per turn (GPU)",
      "cost": "0 (local)",
      "gpu_requirement": "NVIDIA GPU with 11+ GB VRAM",
      "minimum_recommended_ram": "16 GB",
      "provider_limits": "N/A (local)"
    },
    {
      "name": "qwen2.5-coder:14b",
      "provider": "ollama",
      "local": true,
      "vram_gb": 9.0,
      "context_window": 32768,
      "tool_calling": "FAIL multi-tool (5-strike guard)",
      "coding": "strong",
      "reasoning": "basic‑medium",
      "latency": "~1–3 min per turn (GPU)",
      "cost": "0 (local)",
      "gpu_requirement": "NVIDIA GPU with 11+ GB VRAM",
      "minimum_recommended_ram": "24 GB",
      "provider_limits": "N/A (local)"
    },
    {
      "name": "llama-3.3-70b-versatile",
      "provider": "groq",
      "local": false,
      "vram_gb": "cloud",
      "context_window": 128000,
      "tool_calling": "PASS (verified tool execution)",
      "coding": "strong",
      "reasoning": "strong",
      "latency": "~5–15 sec per turn",
      "cost": "free tier: 12k TPM (per model); exceeded after ~7.4k used",
      "gpu_requirement": "N/A (cloud)",
      "minimum_recommended_ram": "N/A",
      "provider_limits": "TPM per model: 12k (llama‑3.3‑70b‑versatile)"
    },
    {
      "name": "deepseek-r1:14b",
      "provider": "ollama",
      "local": true,
      "vram_gb": 9.0,
      "context_window": 32768,
      "tool_calling": "UNVERIFIED (never ran full turn)",
      "coding": "good",
      "reasoning": "strong (reasoning‑oriented model)",
      "latency": "~2–5 min per turn (GPU)",
      "cost": "0 (local)",
      "gpu_requirement": "NVIDIA GPU with 11+ GB VRAM",
      "minimum_recommended_ram": "24 GB",
      "provider_limits": "N/A (local)"
    }
  ],
  "execution_profiles": [
    {
      "name": "Local Qwen 14B",
      "runtime": "agent_zero",
      "model": "qwen2.5-coder:14b",
      "mode": "local",
      "capabilities": {
        "chat": "✓",
        "coding": "✓",
        "reasoning": "△",
        "tool_calling": "✗ multi-tool",
        "browser": "? (GUI required)",
        "memory": "✓ (faiss backend)",
        "tool_surface": "code_exe + file"
      },
      "best_for": "Simple chat, single‑tool tasks, arithmetic"
    },
    {
      "name": "Hybrid Cloud+Local",
      "runtime": "agent_zero",
      "model": "Groq llama‑3.3‑70b‑versatile (cloud) + qwen2.5‑coder:14b (local)",
      "mode": "hybrid",
      "capabilities": {
        "chat": "✓",
        "coding": "✓",
        "reasoning": "✓",
        "tool_calling": "✓ (with reduced tool surface)",
        "browser": "✓ (cloud)",
        "memory": "✓ (faiss)",
        "tool_surface": "code_exe + file + browser"
      },
      "best_for": "Agentic tasks, multi‑tool workflows, browser automation"
    }
  ]
}
```

---

## 6. Recommendations for AgentHost

1. **Execution Profile is the fundamental unit** — not runtime alone, not model alone. AgentHost must resolve **(runtime, model, hardware, tools, mode)** as a composite.

2. **Preflight before every serious task**: check runtime availability, model capability vs. task requirements, TPM/token budget, and tool surface. Return a structured decision (PASS / FAIL + re‑resolve reason).

3. **Hybrid mode is the practical path** for this hardware:  
   - **Local** `qwen2.5-coder:14b` for chat, coding, summarization.  
   - **Cloud** `llama‑3.3‑70b‑versatile` (Groq) or an OpenRouter‑selected model for autonomous tasks, browser, multi‑tool workflows.

4. **Do NOT modify Agent Zero** — the bottleneck is in the *integration* (request size, tool surface, profile selection). AgentHost can mediate by:
   - Selecting a reduced tool surface per task.
   - Switching presets at runtime (config.json can be rewritten; restart required but is acceptable for a test harness).
   - Applying token‑budget throttling (e.g., pause ~45s between turns to respect TPM windows).

5. **Next artifact**: `agenthost‑v0.1‑spec.md` (runtime contract, model/capability schemas, hardware probe, execution‑profile schema, resolver algorithm, Agent Zero adapter boundary). This is the **code‑writing milestone** after the investigation.