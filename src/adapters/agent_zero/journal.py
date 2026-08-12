import urllib.request
import json
from ...domain.contract.runtime_adapter import Journal
from ...domain.errors import RuntimeError

class JournalExtractor:
    def __init__(self, endpoint: str = "http://127.0.0.1:5000/api"):
        self.endpoint = endpoint

    def extract(self, context_id: str) -> Journal:
        url = f"{self.endpoint}/api_log_get?context_id={context_id}"
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    logs = data.get("logs", [])
                    return Journal(logs=logs)
                else:
                    raise RuntimeError(f"Log endpoint returned {response.status}")
        except Exception as e:
            return Journal(logs=[f"[ERROR] Failed to extract logs for context '{context_id}': {str(e)}"])
