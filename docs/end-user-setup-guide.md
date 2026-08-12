# AgentHost v0.1: End-User Setup & Testing Playbook

Welcome to the **AgentHost v0.1** testing phase! This guide will walk you through installing, configuring, and testing AgentHost on a clean Windows machine. 

AgentHost is designed as a **headless infrastructure daemon** and CLI utility. Its goal is to dynamically evaluate your hardware, discover available AI models, and recommend or execute the most reliable execution profile for any given task.

## What UI Should I Expect?

**There is no Graphical User Interface (GUI) or Web Dashboard in v0.1.** 
AgentHost operates entirely via the command-line interface (CLI) in your terminal (PowerShell or Command Prompt). You will interact with it by typing commands and reading structured, human-readable terminal output. 

---

## 1. Prerequisites (The "Clean Machine" Setup)

AgentHost works best when it has a local runtime and local models to choose from, but it can fall back to the cloud. To test the full capability on your Windows machine, ensure you have the following installed:

1. **Python 3.10+**: Ensure Python is added to your system `PATH`.
2. **Docker Desktop**: Required to run the Agent Zero runtime securely in an isolated container.
   - *Ensure the Docker daemon is running before proceeding.*
3. **Ollama (Optional but Recommended)**: Required to test local model execution.
   - Download and install from [ollama.com](https://ollama.com).
   - Pull at least one local model (e.g., `ollama pull qwen:7b` or `ollama pull llama3.3:70b`).

---

## 2. Installation

Open PowerShell or Command Prompt and clone the repository:

```powershell
git clone https://github.com/your-repo/agenthost.git
cd agenthost

# Install dependencies (Optional: create a virtual environment first)
pip install -r requirements.txt
```

---

## 3. The Setup Wizard

The first step is to run the setup wizard. This initializes your environment, generates configuration files, and securely stores any API keys for cloud fallback providers.

```powershell
python -m src.cli.setup
```

**What to expect:**
- The wizard will prompt you for optional API keys (e.g., Groq, OpenAI).
- It will verify your Docker connection.
- If anything fails, it will provide a friendly error message, not a Python stack trace.

---

## 4. Discovery & Diagnostics

Before running tasks, you can inspect what AgentHost has discovered about your machine.

### Run the Hardware & Model Scanner
```powershell
python -m src.cli.scan
```
**What to expect:** A fast (<5 second) JSON or structured output detailing your CPU, RAM, estimated VRAM, and a list of discovered local (Ollama) and cloud models.

### Run the System Doctor
```powershell
python -m src.cli.doctor
```
**What to expect:** A health report identifying any missing daemons (like Docker being offline) or missing environment variables.

---

## 5. The Recommendation Engine

This is the core of AgentHost. Let's see how it decides to route a task based on your hardware, the task requirements, and your configured user policy.

```powershell
python -m src.cli.recommend "write a python script to scrape a website"
```

**What to expect:**
AgentHost will analyze the task (e.g., recognizing it requires coding and browser tools) and output a detailed explanation of its decision in under 3 seconds:

```text
AgentHost Recommendation Engine

Recommended configuration

Runtime
  Agent_zero 2.8

Model
  qwen:14b

Mode
  Local

Why?
  ✓ Score: 1.50
  ✓ Hardware fit: PASS
  ✓ Capabilities fit: PASS
  ✓ Local model is sufficient → use local.

Alternative
  llama3.3:70b (Local)

Confidence
  95%
```

**Test Failure Scenarios:** Try shutting down Docker or Ollama and running the command again. You should receive a friendly formatted message offering actionable alternatives (like falling back to a cloud model).

---

## 6. Task Execution

To actually execute a task, use the `run` command. This will invoke the Execution Profile Resolver, run the Preflight checks (ensuring sufficient RAM/VRAM), and dispatch the task to the Agent Zero container.

```powershell
python -m src.cli.run "write a simple python script to print hello world"
```

**What to expect:**
- If Preflight fails (e.g., you try to load a 70B model into 8GB of VRAM), it will gracefully abort and tell you why.
- If it passes, the task is handed to Agent Zero, and you will see the execution logs/results printed to your terminal.

---

## 7. Next Steps

AgentHost v0.1 is currently **Frozen**. It provides rock-solid orchestration infrastructure. The next development phase (AlamiaAI) will build on top of this foundation to introduce persistence, task inboxes, proactive monitoring, and an eventual user interface.
