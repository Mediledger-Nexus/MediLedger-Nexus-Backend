#!/bin/bash

# MediLedger Nexus Backend Startup Script
# This script sets up the Python path and starts the FastAPI application

# Change to the backend directory
cd "$(dirname "$0")"

# Set the Python path to include the src directory
export PYTHONPATH="$(pwd)/src:${PYTHONPATH}"

# Start the FastAPI application
exec uvicorn mediledger_nexus.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
