#!/usr/bin/env python3
"""
Makitox Platform Launcher
Handles setup and starts the unified server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import aiohttp
        import beautifulsoup4
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    api_dir = Path(__file__).parent / "api"
    requirements_file = api_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def main():
    """Main launcher function"""
    print("🚀 Makitox Platform Launcher")
    print("=" * 40)
    print("💻 Optimized for Mac & Linux")
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    if not (current_dir / "index.html").exists():
        print("❌ Error: index.html not found in current directory")
        print("💡 Make sure you're running this from the project root")
        print("💡 Directory should contain: index.html, api/, etc.")
        return 1
    
    if not (current_dir / "api").exists():
        print("❌ Error: api/ directory not found")
        print("💡 Make sure the api directory exists with server files")
        return 1
    
    print("✅ Project structure looks good")
    
    # Check dependencies
    if not check_dependencies():
        print("⚠️  Missing dependencies, installing...")
        if not install_dependencies():
            print("\n❌ Failed to install dependencies")
            print("💡 Try manually: pip install -r api/requirements.txt")
            return 1
    
    print("✅ Dependencies ready")
    print()
    
    # Start the server
    print("🌟 Starting Makitox unified server...")
    
    try:
        # Import and run server
        from server import app
        import uvicorn
        
        print("📍 Website: http://localhost:8000")
        print("📍 API: http://localhost:8000/api")
        print("📍 Status: http://localhost:8000/api/status")
        print("-" * 40)
        print("💡 Press Ctrl+C to stop")
        print()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Check the error details above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)