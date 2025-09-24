#!/usr/bin/env python3
"""
WSGI entry point for MediLedger Nexus Backend
This file is used by deployment platforms like Render to start the application
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the FastAPI app
from mediledger_nexus.main import app

# Export the app for WSGI servers
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
