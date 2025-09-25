#!/bin/bash

# MediLedger Nexus Startup Script for Render
# This script ensures the correct start command is used

echo "Starting MediLedger Nexus with gunicorn..."

# Set environment variables if not set
export SECRET_KEY=${SECRET_KEY:-"default-secret-key-change-in-production"}
export ENCRYPTION_KEY=${ENCRYPTION_KEY:-"default-encryption-key-change-in-production"}
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./mediledger_nexus.db"}

# Start the application with gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --worker-class uvicorn.workers.UvicornWorker
