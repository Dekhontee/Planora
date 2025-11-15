#!/bin/bash
# run_frontend.sh - Start Planora Streamlit frontend

cd "$(dirname "$0")"
echo "Starting Planora Streamlit frontend..."
echo "Make sure backend is running at http://localhost:8000"
streamlit run streamlit_app.py
