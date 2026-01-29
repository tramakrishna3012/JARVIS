"""
JARVIS Backend - Vercel Entrypoint
"""
import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

# Import the FastAPI app
from app.server import app

# This 'app' variable is what Vercel's @vercel/python runtime looks for
