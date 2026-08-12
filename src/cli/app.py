import argparse
import sys
import threading
import time
import webbrowser
from src.web.server import start_server

def main():
    parser = argparse.ArgumentParser(description="AgentHost Web UI Launcher")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the web server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind to")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()

    print(f"Starting AgentHost Web UI on http://{args.host}:{args.port}")
    
    server_thread = threading.Thread(target=start_server, args=(args.port, args.host))
    server_thread.daemon = True
    server_thread.start()
    
    if not args.no_browser:
        print("Opening browser...")
        # Give the server a moment to start
        time.sleep(1)
        webbrowser.open(f"http://{args.host}:{args.port}")
        
    print("Press Ctrl+C to stop the server.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping AgentHost Web UI...")
        sys.exit(0)

if __name__ == "__main__":
    main()
