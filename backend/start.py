#!/usr/bin/env python3
"""
Startup script for CV Transform API
"""
import uvicorn
import os
from pathlib import Path

def main():
    # Create necessary directories
    uploads_dir = Path("uploads")
    temp_dir = Path("temp")
    
    uploads_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)
    
    # Configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting CV Transform API on {host}:{port}")
    print(f"Upload directory: {uploads_dir.absolute()}")
    print(f"Temp directory: {temp_dir.absolute()}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
