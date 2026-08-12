PS C:\Users\ali\testing-agenthost> git clone https://github.com/AlamiaSoft/alamia-personal-ai.git
Cloning into 'alamia-personal-ai'...
remote: Enumerating objects: 260, done.
remote: Counting objects: 100% (260/260), done.
remote: Compressing objects: 100% (188/188), done.
remote: Total 260 (delta 74), reused 244 (delta 58), pack-reused 0 (from 0)
Receiving objects: 100% (260/260), 184.52 KiB | 1.13 MiB/s, done.
Resolving deltas: 100% (74/74), done.
PS C:\Users\ali\testing-agenthost> python -m src.cli.setup
C:\Users\ali\AppData\Local\Programs\Python\Python312\python.exe: Error while finding module specification for 'src.cli.setup' (ModuleNotFoundError: No module named 'src')
PS C:\Users\ali\testing-agenthost> cd .\alamia-personal-ai\
PS C:\Users\ali\testing-agenthost\alamia-personal-ai> pip install -r requirements.txt
Requirement already satisfied: pydantic>=2.0.0 in c:\users\ali\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 1)) (2.13.4)
Requirement already satisfied: annotated-types>=0.6.0 in c:\users\ali\appdata\local\programs\python\python312\lib\site-packages (from pydantic>=2.0.0->-r requirements.txt (line 1)) (0.8.0)
Requirement already satisfied: pydantic-core==2.46.4 in c:\users\ali\appdata\local\programs\python\python312\lib\site-packages (from pydantic>=2.0.0->-r requirements.txt (line 1)) (2.46.4)
Requirement already satisfied: typing-extensions>=4.14.1 in c:\users\ali\appdata\local\programs\python\python312\lib\site-packages (from pydantic>=2.0.0->-r requirements.txt (line 1)) (4.16.0)
Requirement already satisfied: typing-inspection>=0.4.2 in c:\users\ali\appdata\local\programs\python\python312\lib\site-packages (from pydantic>=2.0.0->-r requirements.txt (line 1)) (0.4.2)

[notice] A new release of pip is available: 25.0.1 -> 26.2.1
[notice] To update, run: python.exe -m pip install --upgrade pip
PS C:\Users\ali\testing-agenthost\alamia-personal-ai> python -m src.cli.setup
=== AgentHost Setup Wizard ===

1. Cloud Provider Configuration
   AgentHost can fall back to cloud providers if your local hardware is insufficient.
   Enter your Groq API Key (or press Enter to skip):
   Enter your OpenAI API Key (or press Enter to skip):
   [OK] Local-only mode enabled and persisted in .env

2. Environment Verification
   [OK] Docker connection verified.
   [OK] Ollama available (8 local models discovered).
   [--] Cloud providers: Disabled (Local-only mode active).

Setup complete. AgentHost is ready to accept tasks.
PS C:\Users\ali\testing-agenthost\alamia-personal-ai> python -m src.cli.scan
=== AgentHost Host Inventory ===

[Hardware]
CPU Cores: 12
System RAM: 31.86 GB
GPU Model: NVIDIA GeForce GTX 1080 Ti
VRAM: 11.0 GB
Disk Space: 159.31 GB

[Environment]
os_name: Windows
os_release: 11
os_version: 10.0.26200
machine: AMD64
docker_running: True
python_version: 3.12.10

[Models] (8 discovered)
- ollama/bge-m3:latest (Provider: ollama, Type: local)
- ollama/gemma3:1b-it-qat (Provider: ollama, Type: local)
- ollama/qwen3.5:4b (Provider: ollama, Type: local)
- ollama/qwen2.5-coder:7b (Provider: ollama, Type: local)
- ollama/qwen2.5:7b (Provider: ollama, Type: local)
- ollama/qwen2.5-coder:1.5b (Provider: ollama, Type: local)
- ollama/qwen2.5-coder:14b (Provider: ollama, Type: local)
- ollama/deepseek-r1:14b (Provider: ollama, Type: local)
PS C:\Users\ali\testing-agenthost\alamia-personal-ai> python -m src.cli.doctor
=== AgentHost Doctor ===
Running diagnostic checks...

[PASS] Docker is installed and running.
[PASS] VRAM check passed (11.0 GB available).
[PASS] 8 models found.

Diagnostic complete.
PS C:\Users\ali\testing-agenthost\alamia-personal-ai> python -m src.cli.recommend "write a python script to scrape a website"
AgentHost Recommendation Engine

No suitable profile found.
Elapsed: 0.30s
PS C:\Users\ali\testing-agenthost\alamia-personal-ai>