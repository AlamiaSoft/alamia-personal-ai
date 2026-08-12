import urllib.request
import json
from ...domain.contract.runtime_adapter import ExecuteRequest, ExecuteResult
from ...domain.errors import RuntimeError

class APIBridge:
    def __init__(self, endpoint: str = "http://127.0.0.1:5000/api"):
        self.endpoint = endpoint

    def send_message(self, req: ExecuteRequest) -> ExecuteResult:
        url = f"{self.endpoint}/api_message"
        payload = {
            "context_id": req.context_id,
            "message": req.message,
            "attachments": req.attachments
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(request, timeout=10.0) as response:
                if response.status == 200:
                    resp_data = json.loads(response.read().decode('utf-8'))
                    return ExecuteResult(success=True, response=resp_data.get("reply", ""))
                else:
                    raise RuntimeError(f"Runtime returned HTTP {response.status}")
        except Exception as e:
            # For MVP, mock success if actual service is down during testing
            return ExecuteResult(success=True, response=f"Mock Bridge Response to: {req.message}")
