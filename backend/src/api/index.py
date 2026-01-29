import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Robust Python Entrypoint for Vercel (Version 3.2 Check)
# attempts to load FastAPI 'app', falls back to JSON error reporting if imports fail.

app = None

try:
    # Add backend root to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    
    # Try importing the main application
    from app.server import app
    print("Successfully imported app.server")

except Exception as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    # Capture error for fallback handler
    sys.modules['init_error'] = e

# Catch-all Handler (used if Vercel doesn't find 'app' or if we want to force handling)
# Note: @vercel/python prefers 'app' variable, but will use 'handler' class if 'app' is not found/callable.
# We expose 'app' if it exists.

if not app:
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error = sys.modules.get('init_error', 'Unknown Error')
            msg = {
                "error": "Backend failed to start",
                "detail": str(error),
                "type": type(error).__name__ if not isinstance(error, str) else "Error"
            }
            self.wfile.write(json.dumps(msg).encode('utf-8'))
        
        # Handle other verbs to avoid 501
        def do_POST(self): self.do_GET()
        def do_OPTIONS(self): self.do_GET()
