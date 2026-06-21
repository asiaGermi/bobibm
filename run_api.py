#!/usr/bin/env python3
"""
API Runner Script for Financial Risk Management System

This script starts the FastAPI application with uvicorn.
Run with: python run_api.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# Made with Bob
