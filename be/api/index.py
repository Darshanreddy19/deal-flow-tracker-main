"""
Vercel Serverless Function Handler for FastAPI
Converts FastAPI app to work with Vercel's serverless environment
"""

import sys
from pathlib import Path

# Add parent directory to path to import main app
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from main import app as fastapi_app

# Ensure CORS is properly configured for Vercel
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export as 'app' for Vercel
app = fastapi_app
