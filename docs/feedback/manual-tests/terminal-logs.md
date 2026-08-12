PS C:\Users\ali\testing-agenthost\alamia-personal-ai> cd..
PS C:\Users\ali\testing-agenthost> git clone https://github.com/AlamiaSoft/alamia-personal-ai.git
Cloning into 'alamia-personal-ai'...
remote: Enumerating objects: 226, done.
remote: Counting objects: 100% (226/226), done.
remote: Compressing objects: 100% (174/174), done.
remote: Total 226 (delta 48), reused 216 (delta 38), pack-reused 0 (from 0)
Receiving objects: 100% (226/226), 176.98 KiB | 579.00 KiB/s, done.
Resolving deltas: 100% (48/48), done.
PS C:\Users\ali\testing-agenthost> cd .\alamia-personal-ai\
PS C:\Users\ali\testing-agenthost\alamia-personal-ai> python -m src.cli.setup
=== AgentHost Setup Wizard ===

1. Cloud Provider Configuration
   AgentHost can fall back to cloud providers if your local hardware is insufficient.
   Enter your Groq API Key (or press Enter to skip):
   Enter your OpenAI API Key (or press Enter to skip):
   [OK] Skipping cloud configuration. Local-only mode enabled.

2. Environment Verification
   [OK] Docker connection verified.
   [OK] Scanned environment and found 414 models.

Setup complete. AgentHost is ready to accept tasks.
PS C:\Users\ali\testing-agenthost\alamia-personal-ai>
