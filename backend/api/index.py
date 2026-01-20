import os
import sys

# Standard entrypoint for Vercel Python
# Adds backend root to sys.path to find 'app' module

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

    from app.main import app
except Exception as e:
    # Fallback to show error if imports fail
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "OPTIONS"])
    async def catch_all(path_name: str):
        return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})
