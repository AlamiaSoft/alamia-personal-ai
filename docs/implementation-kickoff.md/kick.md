# AgentHost — v0.1 Implementation Kickoff

You are implementing AgentHost, an agent-agnostic local AI orchestration/host platform.

IMPORTANT:
This is NOT an Agent Zero wrapper.
Agent Zero is the first runtime adapter only.

The product principle is:

    AgentHost is the product.
    AI runtimes, models, providers, and tools are replaceable infrastructure.

The goal is to create a highly usable/adoptable system that can inspect a user's machine, understand available AI capabilities, select the most suitable execution configuration, install/configure the required runtime, validate it, and provide a unified interface.

============================================================
SOURCE OF TRUTH
============================================================

Before writing implementation code, inspect the repository and read these documents completely:

    docs/agent-zero-evaluation.md
    docs/agent-zero-capability-matrix.md
    docs/agent-zero-installation.md
    docs/agent-zero-security.md
    docs/agenthost-plan.md
    docs/model-bottleneck-investigation.md
    artifacts/environment-report.json
    artifacts/runtime-report.json
    artifacts/capability-report.json
    artifacts/model-profiles.json

Also inspect any existing repository conventions, README, AGENTS.md, CLAUDE.md, OpenCode instructions, pyproject.toml, etc.

Treat the above evaluation artifacts as empirical evidence.

DO NOT invent Agent Zero capabilities that were not verified.

DO NOT modify Agent Zero itself.

DO NOT fork or patch Agent Zero.

============================================================
CORE ARCHITECTURE
============================================================

AgentHost v0.1 consists of:

1. Host Discovery
2. Runtime Registry
3. Model Registry
4. Capability/Evidence Registry
5. Execution Profile Resolver
6. Runtime Adapter Contract
7. Agent Zero Adapter
8. Security Boundary
9. Local API
10. CLI

The fundamental decision unit is:

    ExecutionProfile

An ExecutionProfile combines:

    runtime
    model
    hardware
    tools
    capabilities
    mode
    security policy
    cost/privacy constraints

Runtime and Model are NOT independently responsible for making the final execution decision.

The decision flow is:

    User Task
        ↓
    Task Requirements
        ↓
    Hardware Inventory
        ↓
    Runtime Candidates
        ↓
    Model Candidates
        ↓
    Tool Candidates
        ↓
    Capability Evidence
        ↓
    Execution Profile Resolver
        ↓
    Preflight
        ↓
    PASS → Execute
    FAIL → Re-resolve / explain failure

The bootstrap path MUST NOT require an LLM.

Resolution must initially be deterministic, explainable, reproducible and testable.

============================================================
LANGUAGE / IMPLEMENTATION
============================================================

Use Python for the AgentHost local application.

Use modern Python typing.

Use a clean package structure.

Prefer:

    pyproject.toml
    uv
    pytest

Keep dependencies minimal.

Do not introduce heavyweight frameworks unless there is a demonstrated requirement.

The first implementation must work on Windows.

Design platform boundaries so Linux/macOS support can be added later.

Do not introduce Laravel yet.

Laravel is a future cloud/control-plane concern and MUST NOT be required for local AgentHost operation.

============================================================
TARGET STRUCTURE
============================================================

Create/adapt the repository toward:

agent-host/
├── src/
│   └── agenthost/
│       ├── host/
│       │   ├── hardware/
│       │   ├── environment/
│       │   ├── lifecycle/
│       │   ├── diagnostics/
│       │   └── process/
│       │
│       ├── runtime/
│       │   ├── contract/
│       │   ├── registry/
│       │   ├── resolver/
│       │   └── adapters/
│       │       └── agent_zero/
│       │
│       ├── models/
│       │   ├── registry/
│       │   ├── discovery/
│       │   └── resolver/
│       │
│       ├── capabilities/
│       ├── tools/
│       ├── profiles/
│       ├── security/
│       │   ├── permissions/
│       │   ├── secrets/
│       │   ├── sandbox/
│       │   └── audit/
│       │
│       ├── config/
│       ├── api/
│       └── cli/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── contract/
│
├── docs/
├── artifacts/
├── pyproject.toml
└── README.md

Adapt this structure if the existing repository already has an established convention, but preserve the architectural boundaries.

============================================================
PHASE 0 — DOMAIN CONTRACTS
============================================================

Implement the domain contracts first.

Create strongly typed models for:

    HardwareProfile
    EnvironmentProfile
    RuntimeInfo
    RuntimeCapabilities
    ModelProfile
    ModelProvider
    ToolProfile
    Capability
    CapabilityEvidence
    TaskRequirements
    ExecutionProfile
    PreflightResult
    RuntimeHealth
    ExecuteRequest
    ExecuteResult
    RuntimeEvent
    Diagnostics
    ResolutionResult

Use enums/value objects where appropriate rather than arbitrary strings everywhere.

Every model should have:

    stable identifier
    human-readable name
    structured metadata
    provenance/evidence where relevant

============================================================
CAPABILITY EVIDENCE
============================================================

Capability data must distinguish:

    verified
    inferred
    documented
    unknown
    unsupported

Do NOT treat UNKNOWN as SUPPORTED.

Do NOT treat vendor claims as equivalent to AgentHost empirical verification.

Model capability data must support evidence such as:

    source
    test suite
    tested timestamp
    environment
    confidence
    notes

Example conceptual model:

    tool_calling:
        value: true
        evidence:
            source: empirical
            confidence: 0.95
            test: agent-zero-multitool
            status: verified

This is important because the current Agent Zero investigation showed:

    Qwen 7B/14B:
        simple chat/code execution → works
        multi-tool unified-turn → fails

    Llama 3.3 70B:
        tool execution → verified
        cloud TPM constraints → significant

    DeepSeek R1 14B:
        compatibility → currently unverified

Preserve that distinction.

============================================================
HARDWARE DISCOVERY
============================================================

Implement the first real host capability:

    agenthost scan

It should discover at minimum:

    OS
    OS version
    architecture
    CPU
    CPU cores/threads
    RAM
    disk
    GPU
    GPU VRAM when available
    Docker
    Ollama
    Python
    uv
    WSL when applicable

The implementation must be Windows-first.

Use safe subprocess execution.

Never assume a command exists.

A missing dependency should become structured information:

    status = unavailable

rather than crashing discovery.

Output must be machine-readable internally.

Provide JSON serialization.

Example:

    {
      "cpu": {...},
      "memory": {...},
      "gpu": {...},
      "docker": {...},
      "ollama": {...}
    }

============================================================
RUNTIME CONTRACT
============================================================

Implement RuntimeAdapter as the stable boundary between AgentHost and runtimes.

Minimum interface:

    discover()
    install()
    configure()
    start()
    stop()
    restart()
    health()
    capabilities()
    models()
    execute()
    stream()
    cancel()
    logs()
    diagnostics()

Do not put Agent Zero-specific behavior in the generic contract.

The generic contract must remain runtime-agnostic.

============================================================
AGENT ZERO ADAPTER
============================================================

Implement Agent Zero as the first adapter.

Use ONLY the verified integration surface from the evaluation:

Lifecycle:
    Docker lifecycle

Chat:
    POST /api/api_message

Authentication:
    X-API-KEY

Logs:
    /api/api_log_get

Files:
    /api_files_get

Streaming:
    socket.io v4 where verified
    REST fallback where necessary

Reset/terminate:
    verified Agent Zero endpoints

Configuration:
    presets/configuration files and secrets as documented by the evaluation

Version detection:
    image digest/container version information

The adapter must isolate all Agent Zero-specific API paths, payloads and compatibility behavior.

AgentHost core must not contain raw Agent Zero API calls.

============================================================
RUNTIME REGISTRY
============================================================

Create a registry abstraction.

The registry should support:

    register
    unregister
    get
    list
    discover
    status

Represent runtime instances separately from runtime types.

Example:

    RuntimeType:
        agent-zero

    RuntimeInstance:
        agent-zero@docker-local

This distinction matters because users may eventually have:

    Agent Zero local
    Agent Zero remote
    OpenJarvis local
    OpenJarvis WSL
    etc.

============================================================
MODEL REGISTRY
============================================================

Implement a provider-agnostic Model Registry.

First provider:

    Ollama

Support discovery from Ollama's local API.

Do not hardcode only Qwen.

The current test machine happens to contain:

    qwen2.5-coder:7b
    qwen2.5-coder:14b
    deepseek-r1:14b

but AgentHost must discover models dynamically.

Create a model profile structure capable of storing:

    provider
    model id
    context window
    VRAM requirement
    RAM requirement
    coding capability
    reasoning capability
    tool calling capability
    vision capability
    latency
    cost
    TPM
    local/cloud/hybrid
    evidence
    confidence

Do not pretend automatically discovered models have empirically verified capability scores.

Unknown should remain unknown.

============================================================
EXECUTION PROFILES
============================================================

Implement ExecutionProfile as the central composite.

It should combine:

    runtime
    model
    hardware
    tools
    capabilities
    mode
    security policy
    cost
    privacy
    confidence

Example:

    Local Qwen 14B

    runtime:
        agent-zero

    model:
        ollama/qwen2.5-coder:14b

    mode:
        local

    capabilities:
        chat: strong
        coding: strong
        multi_tool: weak

    limitations:
        multi-tool agentic execution not verified/supported

And:

    Hybrid Cloud + Local

    local:
        Ollama

    cloud:
        qualified provider/model

    local tasks:
        chat
        coding
        summarization

    cloud tasks:
        autonomous execution
        browser
        multi-tool

============================================================
RESOLVER
============================================================

Implement deterministic resolution.

No LLM.

Resolution should perform:

1. Hard compatibility filtering.
2. Capability filtering.
3. Hardware filtering.
4. Security/privacy filtering.
5. Cost filtering.
6. Weighted scoring.

Initial runtime weighting from the architecture evidence:

    Hardware Fit       25%
    Capability Fit     25%
    Reliability        20%
    Performance        10%
    Installation Cost  10%
    Privacy            10%

Make weights configurable.

Do not bury them in arbitrary scattered conditionals.

Return an explanation with every resolution.

Example:

    selected:
        agent-zero + ollama/qwen2.5-coder:14b

    reasons:
        - Docker available
        - runtime installed
        - model fits VRAM
        - local inference
        - coding capability verified

    warnings:
        - multi-tool capability insufficient

    rejected:
        ...
        reason: ...

The resolver MUST be explainable.

============================================================
TASK REQUIREMENTS
============================================================

Implement TaskRequirements as a structured object.

For v0.1, do NOT build an LLM task analyzer.

Allow requirements to be explicitly supplied.

Examples:

    browser = true
    filesystem = true
    coding = true
    reasoning = high
    autonomy = high
    vision = false
    privacy = local_only

Later we can add intelligent task classification.

============================================================
PREFLIGHT
============================================================

Implement two levels:

PROFILE PREFLIGHT

Runs when:

    profile selected
    runtime installed
    model changed
    tools changed
    environment changed

TASK PREFLIGHT

Runs cheaply before execution.

Check:

    runtime health
    model availability
    required capabilities
    hardware compatibility
    estimated context requirements where possible
    provider/token limits where known
    security policy

Return:

    PASS
    WARN
    FAIL

Never silently execute with known incompatibilities.

Preflight must explain failures and suggest alternatives.

============================================================
TOKEN / CONTEXT ESTIMATION
============================================================

DO NOT hardcode:

    11300 tokens

as a universal Agent Zero requirement.

The investigation established approximately 11.3k tokens as the tested baseline for the default configuration.

Model this dynamically.

Create a context/token estimation abstraction that can eventually account for:

    system prompt
    runtime prompt
    selected tools
    memory
    conversation
    attachments

For v0.1 it may use estimates rather than exact tokenizer calculations.

Document that limitation.

============================================================
SECURITY
============================================================

Security is not optional.

Implement the abstraction now, even if some backends are initially minimal.

Defaults:

    Read         → allowed
    Write        → confirmation
    Execute      → confirmation
    External     → confirmation
    Destructive  → confirmation + audit

Never expose Agent Zero on 0.0.0.0 by default.

Prefer loopback.

Secrets must never be stored in plain configuration files when a secure store is available.

Create interfaces for:

    SecretStore
    PermissionPolicy
    AuditLogger

A development implementation may be used initially, but clearly mark it as non-production.

============================================================
CLI
============================================================

Implement the first CLI.

Commands:

    agenthost scan
    agenthost doctor
    agenthost runtime list
    agenthost runtime status
    agenthost runtime start
    agenthost runtime stop
    agenthost runtime restart
    agenthost model list
    agenthost profile list
    agenthost recommend
    agenthost preflight
    agenthost chat

Keep output human-friendly but make JSON output possible:

    --json

Example:

    agenthost scan --json

============================================================
TESTING
============================================================

Tests are mandatory.

At minimum:

UNIT:

    hardware parsing
    runtime registry
    model registry
    capability evidence
    scoring
    resolver
    profile validation
    preflight
    token estimation

CONTRACT:

    RuntimeAdapter contract tests

AGENT ZERO:

    mock REST responses
    authentication
    health
    execute
    logs
    configuration
    lifecycle command construction

Do NOT require a live Agent Zero container for normal unit tests.

Live tests should be explicitly marked/invoked separately.

Create fixtures derived from the completed Agent Zero evaluation.

============================================================
IMPLEMENTATION DISCIPLINE
============================================================

Follow this sequence:

PHASE 1
    Inspect repository
    Confirm existing stack
    Create implementation plan

PHASE 2
    Domain schemas/contracts
    Unit tests

PHASE 3
    Host discovery

PHASE 4
    Runtime registry + generic adapter contract

PHASE 5
    Agent Zero adapter

PHASE 6
    Ollama model discovery

PHASE 7
    Execution profiles

PHASE 8
    Resolver

PHASE 9
    Preflight

PHASE 10
    Security abstractions

PHASE 11
    CLI integration

PHASE 12
    End-to-end local validation

After each phase:

    run tests
    inspect failures
    fix them
    update documentation

Do not proceed while the previous phase is fundamentally broken.

============================================================
IMPORTANT NON-GOALS
============================================================

DO NOT implement:

    Laravel
    cloud control plane
    SaaS accounts
    billing
    marketplace
    mobile app
    multi-user management
    remote fleet management
    complex GUI
    LLM-based resolver
    autonomous AgentHost reasoning
    AgentHost memory system
    AgentHost prompt framework

These are future concerns.

DO NOT build OpenJarvis adapter yet.

DO NOT build multiple cloud providers yet.

Ollama + Agent Zero is the initial integration target.

============================================================
QUALITY BAR
============================================================

This must be production-oriented code, not a throwaway prototype.

Requirements:

    typed
    modular
    testable
    documented
    deterministic
    explainable
    platform-aware
    security-conscious

Avoid:

    giant classes
    global mutable state
    hardcoded machine-specific paths
    hardcoded ports
    hardcoded model names
    Agent Zero leakage into core
    provider-specific logic in resolver
    silent fallbacks
    swallowed exceptions

Use structured errors.

Use dependency injection where it actually improves testability.

Do not over-engineer abstractions that have no current consumer.

============================================================
CRITICAL LOCAL MODEL CONSTRAINT
============================================================

The coding environment is currently using local models around:

    qwen2.5:7b
    deepseek 14b

Therefore:

    keep implementation steps small
    avoid massive speculative refactors
    make one coherent change at a time
    run tests frequently
    do not rewrite working code unnecessarily
    do not invent APIs

When uncertain about an implementation detail:

    inspect the repository
    inspect existing documentation
    inspect tests
    use the evidence artifacts
    then implement

Do not guess.

============================================================
FIRST TASK
============================================================

Do NOT immediately implement everything.

First:

1. Inspect the repository.
2. Read all source/evidence documents listed above.
3. Identify the current repository state.
4. Produce a concise implementation plan mapped to the phases above.
5. Identify any conflicts between the current repository and the proposed architecture.
6. Identify missing information that genuinely blocks implementation.
7. Then begin Phase 1.

Once Phase 1 is implemented:

    run the complete test suite
    show the resulting structure
    summarize what was implemented
    identify the next smallest implementation step

Continue implementation autonomously unless a genuine architectural decision or destructive operation requires clarification.

The objective is a working AgentHost v0.1 foundation, not merely documentation.