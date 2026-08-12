# Empirical Lessons from Agent Zero Evaluation

## 1. Prompt Payload Origin (~11.3k Baseline)
The ~11.3k baseline prompt token footprint observed in Agent Zero is produced by the combination of framework profile prompts, 25+ tool schemas, memory context, and turn history. It is **not** an intrinsic minimum requirement of the Agent Zero execution engine itself. 
- **Actionable Takeaway for AgentHost**: Dynamic **Capability-Driven Tool Injection** (injecting only tools required for the immediate task) drastically shrinks prompt overhead, reducing latency and enabling small local models to perform reliably.

## 2. Model Tool-Calling Variance
Local models under 14B parameters show variable multi-tool JSON output reliability, while models like `llama-3.3-70b-versatile` display robust multi-step tool execution.
- **Actionable Takeaway for AgentHost**: Model selection cannot rely on generic vendor claims. Capability scores must be scaled by evidence confidence scores derived from empirical host benchmarks ($effective\_capability = capability\_score \times evidence\_confidence$).

## 3. Windows & Container Nuances
On Windows environments, containerized execution via Docker provides cleanest filesystem isolation and environment reproducibility.
- **Actionable Takeaway for AgentHost**: AgentHost CLI `scan` and `doctor` commands must explicitly verify Docker daemon socket accessibility on Windows and provide automated diagnostic checks.
