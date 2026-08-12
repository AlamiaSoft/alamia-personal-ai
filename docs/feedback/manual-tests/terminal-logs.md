PS C:\Users\ali\testing-agenthost> git clone https://github.com/AlamiaSoft/alamia-personal-ai.git
Cloning into 'alamia-personal-ai'...
remote: Enumerating objects: 130, done.
remote: Counting objects: 100% (130/130), done.
remote: Compressing objects: 100% (111/111), done.
remote: Total 130 (delta 13), reused 126 (delta 9), pack-reused 0 (from 0)
Receiving objects: 100% (130/130), 117.70 KiB | 63.00 KiB/s, done.
Resolving deltas: 100% (13/13), done.
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
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ali\testing-agenthost\alamia-personal-ai\src\cli\setup.py", line 4, in <module>
    from ..cli.formatter import ErrorFormatter, AgentHostError
ImportError: cannot import name 'AgentHostError' from 'src.cli.formatter' (C:\Users\ali\testing-agenthost\alamia-personal-ai\src\cli\formatter.py)
PS C:\Users\ali\testing-agenthost\alamia-personal-ai>