#!/usr/bin/env python3
"""
Startup script for CaiRO Travel API server.
"""

import os
import sys
import multiprocessing
import uvicorn
from main import app

def main():
    """Start the FastAPI server."""
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        print("\nOr add it to your .env file:")
        print("GEMINI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # Calculate optimal number of workers
    # Use CPU count or set a maximum based on your server capacity
    workers = min(multiprocessing.cpu_count(), 8)  # Cap at 8 for memory management
    
    print("🚀 Starting CaiRO Travel API server...")
    print(f"👥 Using {workers} worker processes for parallel processing")
    print("📍 Server will be available at: http://localhost:3001")
    print("📚 API documentation will be available at: http://localhost:3001/docs")
    print("🔧 Alternative docs at: http://localhost:3001/redoc")
    
    # Start the server with multiple workers
    uvicorn.run(
        "main:app",  # Use import string for reload functionality
        host="0.0.0.0",
        port=3001,
        workers=workers,  # Enable multiple worker processes
        log_level="info",
        access_log=True,
        # Remove reload=True when using workers (incompatible)
        # reload=True,  # Commented out - incompatible with workers
    )

if __name__ == "__main__":
    main() 