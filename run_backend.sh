#!/bin/bash
# run_backend.sh - Start Planora FastAPI backend

cd "$(dirname "$0")"
echo "Starting Planora FastAPI backend..."
python3 backend/main.py
