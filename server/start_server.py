#!/usr/bin/env python3
"""
Startup script for CaiRO Travel API server.
"""

import os
import sys
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
    
    print("🚀 Starting CaiRO Travel API server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation will be available at: http://localhost:8000/docs")
    print("🔧 Alternative docs at: http://localhost:8000/redoc")
    
    # Start the server
    uvicorn.run(
        "main:app",  # Use import string for reload functionality
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

if __name__ == "__main__":
    main() 