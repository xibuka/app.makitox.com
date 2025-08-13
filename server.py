#!/usr/bin/env python3
"""
Makitox Unified Server
Run from project root directory
"""

import sys
from pathlib import Path

# Add api directory to Python path
current_dir = Path(__file__).parent
api_dir = current_dir / "api"
sys.path.insert(0, str(api_dir))

# Import and configure the integrated server
from integrated_server import app
import uvicorn
import os

# Update paths for root execution
os.chdir(current_dir)

# Override static directory path for root execution
import integrated_server
integrated_server.STATIC_DIR = "./"  # Website files in current directory
integrated_server.setup_static_files()  # Re-setup static file mounts with new path

if __name__ == "__main__":
    print("🌟 Starting Makitox Platform...")
    print("💻 Optimized for Mac & Linux")
    print("📍 Website: http://localhost:8000")
    print("📍 API: http://localhost:8000/api")
    print("📍 Status: http://localhost:8000/api/status")
    print("📍 Gold Prices: http://localhost:8000/api/gold-prices/yearly")
    print("-" * 50)
    print("💡 Press Ctrl+C to stop the server")
    print()
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Makitox server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you're in the project root directory")
        print("💡 And run: pip install -r api/requirements.txt")
        print("💡 This platform is optimized for Mac & Linux systems")