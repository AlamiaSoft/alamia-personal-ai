You're right to be dissatisfied. **This is not production-grade model discovery.** It's essentially a hand-written model database disguised as a scanner.

The worst problems aren't even the hardcoded numbers themselves; they're the **false evidence claims** attached to them.

### The biggest red flags

```python
reasoning_score = 0.78
coding_score = 0.85
tool_score = 0.80
```

Those are guesses based on model names.

And then:

```python
evidence=Evidence(
    source="empirical",
    tested=True,
    confidence=0.85
)
```

That's particularly bad.

**A model being discovered from Ollama does not mean it was empirically tested.**

Likewise:

```python
id="openai/gpt-4o"
```

doesn't mean that model is actually available to the user, and:

```python
limits=Limits(tpm=300000)
```

isn't something the scanner has verified.

This violates the principle we established earlier:

> **Provider metadata ≠ hardware estimate ≠ empirical capability.**

---

# What ModelScanner should actually do

I'd redesign it around **three layers of evidence**.

```text
                 Model Discovery
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Provider API     Local Runtime    Empirical
    metadata         metadata        probing
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  ModelProfile
                       │
                Evidence attached
                to EVERY capability
```

### 1. Discovery

Find what actually exists.

For Ollama:

```text
GET /api/tags
GET /api/show
```

You should obtain things like:

* model name
* digest
* size
* parameter size
* quantization
* family
* format
* context information where exposed
* capabilities where exposed
* template
* modified timestamp

Don't infer these from `"14b"` appearing in the filename.

---

### 2. Provider metadata

For cloud providers, **query the provider/API rather than assuming models**.

For example:

```text
GROQ_API_KEY exists
        ↓
authenticate
        ↓
GET available models
        ↓
actual model IDs
        ↓
provider metadata
```

Same concept for OpenAI, Anthropic, OpenRouter, etc.

If the API cannot provide something:

```text
value = UNKNOWN
evidence = provider_metadata_missing
confidence = 0
```

**Never fabricate it.**

---

### 3. Empirical capability probing

This is where your earlier `empirical_capabilities.json` becomes important.

Don't say:

```python
tool_calling=0.88
```

because it's Llama 3.3.

Instead, actually test:

```text
basic_chat
structured_output
tool_calling
multi_tool_call
code_generation
reasoning
vision
long_context
```

Obviously you don't need to run every expensive probe every time.

Cache the results:

```text
model
digest/version
probe_suite_version
timestamp
→ capability evidence
```

So:

```text
qwen2.5-coder:14b
digest: abc123
tool_calling:
    supported: true
    confidence: 0.92
    evidence: empirical
    tested_at: ...
```

That's a **real capability profile**.

---

# Hardware requirements are another problem

This:

```python
if "14b" in param_size:
    vram_req = 10.0
    ram_req = 12.0
```

is too simplistic.

A 14B model could be:

```text
Q4
Q5
Q8
FP16
```

and have radically different memory requirements.

Ollama already knows the actual model size.

Use the actual artifact size as the starting point.

Better:

```text
model disk size
+
quantization
+
runtime overhead
+
context allocation
+
KV cache estimate
```

Then produce:

```text
estimated_vram
estimated_ram
confidence
```

rather than pretending `14B = 10GB VRAM`.

And ideally distinguish:

```text
minimum
recommended
comfortable
```

---

# Context window is currently dangerously fake

You're doing:

```python
Context(window=8192)
```

for **every Ollama model**.

That's unacceptable for a system whose entire purpose is intelligent model selection.

The scanner should obtain context information from the runtime/model metadata where possible.

If it can't:

```text
context_window = UNKNOWN
```

Then the resolver must account for that uncertainty.

---

# Cloud models need the same treatment

This:

```python
if os.environ.get("OPENAI_API_KEY"):
    cloud_models.append(
        ModelProfile(id="openai/gpt-4o", ...)
    )
```

means:

> "If the user has an OpenAI key, pretend GPT-4o is available."

That's not discovery.

It's a **hardcoded recommendation list**.

You want:

```text
Credential detected
       ↓
Provider adapter
       ↓
Authenticate
       ↓
List available models
       ↓
Normalize provider metadata
       ↓
ModelProfile
```

And provider-specific rate limits should ideally be queried or represented as **unknown**, not invented.

---

# I would change the architecture

Don't make `ModelScanner` responsible for knowing everything.

Something closer to:

```text
src/
├── discovery/
│   ├── model_scanner.py
│   └── providers/
│       ├── ollama.py
│       ├── openai.py
│       ├── anthropic.py
│       ├── groq.py
│       └── openrouter.py
│
├── capabilities/
│   ├── probe_engine.py
│   ├── probe_suite.py
│   └── evidence.py
│
└── models/
    ├── normalizer.py
    └── registry.py
```

Then:

```text
ProviderAdapter
       ↓
RawModel
       ↓
Normalizer
       ↓
ModelProfile
       ↓
CapabilityProbe
       ↓
Evidence-enriched ModelProfile
       ↓
Registry
```

That is much more consistent with the AgentHost architecture you've been building.
