import os
import sys

# Add the parent directory to sys.path so 'app' package is visible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel expects 'app' to be the WSGI/ASGI application
