#!/usr/bin/env python3
"""
Simple script to run Solvely Lite with Uvicorn
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir("/home/runner/workspace")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )