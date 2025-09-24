#!/bin/bash

# MediLedger Nexus Backend Startup Script
# This script sets up the Python path and starts the FastAPI application

# Set the Python path to include the src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Change to the backend directory
cd "$(dirname "$0")"

# Start the FastAPI application
exec uvicorn src.mediledger_nexus.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
