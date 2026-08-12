import json
import logging
import os
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Ensure the parent directory is in sys.path if running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.discovery.inventory import InventoryBuilder
from src.resolution.resolver import ExecutionProfileResolver
from src.resolution.task_analyzer import TaskAnalyzer
from src.domain.schemas.user_policy import UserPolicy
# Diagnostics Inspector? Need to check if there's a DiagnosticsInspector class or I should just copy from doctor.py

# Path to static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("agenthost.web")

class AgentHostAPIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Handle API routes
        if parsed_path.path.startswith("/api/"):
            return self.handle_api_get(parsed_path)
            
        # Fallback to static file serving
        # Redirect root to index.html
        if self.path == "/":
            self.path = "/index.html"
            
        # SPA routing: if requesting a path that doesn't exist and doesn't have an extension, serve index.html
        local_path = os.path.join(STATIC_DIR, self.path.lstrip("/"))
        if not os.path.exists(local_path) and not "." in os.path.basename(self.path):
            self.path = "/index.html"
            
        return super().do_GET()
        
    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith("/api/"):
            return self.handle_api_post(parsed_path)
            
        self.send_error(405, "Method Not Allowed")

    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
        
    def _send_error_response(self, error_msg, status=500):
        self._send_json_response({"error": error_msg}, status)

    def handle_api_get(self, parsed_path):
        route = parsed_path.path
        
        try:
            if route == "/api/scan":
                builder = InventoryBuilder()
                inventory = builder.build()
                
                # We need to convert Pydantic models to dict to serialize
                return self._send_json_response({
                    "hardware": inventory.hardware.model_dump(),
                    "models": [m.model_dump() for m in inventory.models],
                    "os_environment": inventory.os_environment
                })
                
            elif route == "/api/doctor":
                # Implement diagnostics similar to doctor.py
                builder = InventoryBuilder()
                inventory = builder.build()
                
                results = []
                # Check Docker
                if inventory.os_environment.get("docker_running", False):
                    results.append({"check": "Docker", "status": "PASS", "message": "Docker is installed and running."})
                else:
                    results.append({"check": "Docker", "status": "FAIL", "message": "Docker is not running or not accessible."})
                
                # Check VRAM
                vram = inventory.hardware.vram_gb
                if vram is None or vram < 4.0:
                    results.append({"check": "VRAM", "status": "WARN", "message": f"Low VRAM detected (Found: {vram} GB)."})
                else:
                    results.append({"check": "VRAM", "status": "PASS", "message": f"{vram} GB available."})
                    
                # Check Models
                if len(inventory.models) > 0:
                    results.append({"check": "Models", "status": "PASS", "message": f"{len(inventory.models)} models found."})
                else:
                    results.append({"check": "Models", "status": "WARN", "message": "No models discovered."})
                    
                return self._send_json_response({"diagnostics": results})
                
            elif route == "/api/config":
                # Mock config returning for now
                return self._send_json_response({"mode": "hybrid", "theme": "nova"})
                
            else:
                self._send_error_response("Not Found", 404)
        except Exception as e:
            logger.error(f"Error handling GET {route}: {e}")
            self._send_error_response(str(e))

    def handle_api_post(self, parsed_path):
        route = parsed_path.path
        
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
            
            if route == "/api/recommend":
                task = payload.get("task", "general task")
                
                builder = InventoryBuilder()
                inventory = builder.build()
                
                analyzer = TaskAnalyzer()
                reqs = analyzer.analyze(task)
                
                policy = UserPolicy()
                resolver = ExecutionProfileResolver()
                profiles, explainability = resolver.resolve(inventory, reqs, [], policy)
                
                if not profiles:
                    return self._send_json_response({"error": "No suitable profile found."}, 404)
                    
                top_profile = profiles[0]
                is_verified = top_profile.model.evidence.confidence > 0.40
                
                reasons = explainability.get(top_profile.model.id, [])
                
                response_data = {
                    "runtime": f"{top_profile.runtime_id.capitalize()} 2.8",
                    "model": top_profile.model.id,
                    "mode": top_profile.model.provider.type.capitalize(),
                    "is_verified": is_verified,
                    "suitability_status": "Empirically Verified Capable Candidate" if is_verified else "Best structural candidate -- capability unverified",
                    "explainability": reasons,
                    "confidence_score": (top_profile.reliability_score * 100) if is_verified else 0,
                    "estimated_cost": top_profile.model.economics.cost_per_1m_input,
                    "alternatives": []
                }
                
                if len(profiles) > 1:
                    alt_profile = profiles[1]
                    response_data["alternatives"].append({
                        "model": alt_profile.model.id,
                        "mode": alt_profile.model.provider.type.capitalize()
                    })
                    
                return self._send_json_response(response_data)
                
            elif route == "/api/setup":
                # Mock setup persistence
                return self._send_json_response({"status": "success", "message": "Settings saved"})
                
            elif route == "/api/run":
                return self._send_json_response({"status": "queued", "task": payload.get("task")})
                
            else:
                self._send_error_response("Not Found", 404)
        except Exception as e:
            logger.error(f"Error handling POST {route}: {e}")
            self._send_error_response(str(e))

def start_server(port=8000, bind="127.0.0.1"):
    # Ensure static directory exists
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    server_address = (bind, port)
    httpd = HTTPServer(server_address, AgentHostAPIHandler)
    logger.info(f"Starting AgentHost Web API Server on http://{bind}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
