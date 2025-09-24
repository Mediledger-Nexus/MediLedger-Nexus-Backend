#!/usr/bin/env python3
"""
Main application entry point for MediLedger Nexus Backend
This file is used by Render for automatic deployment detection
"""

import os
import sys

# Add the backend/src directory to Python path
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_path)

# Import the FastAPI app
from mediledger_nexus.main import app

# Export the app for deployment platforms
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
