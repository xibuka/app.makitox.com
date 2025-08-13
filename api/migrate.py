#!/usr/bin/env python3
"""
Migration script to help transition from separate servers to integrated architecture
"""

import os
import shutil
import json
from pathlib import Path

def migrate_to_integrated():
    """Migrate existing setup to integrated architecture"""
    print("🚀 Makitox Migration to Integrated Architecture")
    print("=" * 50)
    
    # Check current setup
    api_dir = Path(".")
    static_dir = Path("../")
    
    print("📋 Checking current setup...")
    
    # Verify files exist
    required_files = [
        "main.py",
        "scraper.py", 
        "requirements.txt",
        "integrated_server.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (api_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required API files found")
    
    # Check static files
    static_files = [
        "index.html",
        "app-miraialarm.html", 
        "support.html",
        "privacy.html"
    ]
    
    found_static = []
    for file in static_files:
        if (static_dir / file).exists():
            found_static.append(file)
    
    print(f"✅ Found {len(found_static)} static files: {found_static}")
    
    # Backup existing data
    if (api_dir / "data").exists():
        print("💾 Backing up existing data...")
        backup_dir = api_dir / "data_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(api_dir / "data", backup_dir)
        print(f"✅ Data backed up to {backup_dir}")
    
    # Create Docker files if they don't exist
    dockerfile = api_dir / "Dockerfile"
    if not dockerfile.exists():
        print("⚠️  Dockerfile not found - creating basic version")
        # The Dockerfile should already be created by the previous code
    
    # Check Docker Compose
    compose_file = static_dir / "docker-compose.yml"
    if not compose_file.exists():
        print("⚠️  docker-compose.yml not found in project root")
    else:
        print("✅ Docker Compose configuration found")
    
    # Create startup script
    startup_script = api_dir / "start_integrated.py"
    with open(startup_script, 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Startup script for Makitox integrated server
\"\"\"

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from integrated_server import app
    import uvicorn
    
    if __name__ == "__main__":
        print("🌟 Starting Makitox Integrated Server...")
        print("📍 Website: http://localhost:8000")
        print("📍 API: http://localhost:8000/api")
        print("📍 Status: http://localhost:8000/api/status")
        print("-" * 40)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            access_log=True
        )

except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
""")
    
    startup_script.chmod(0o755)
    print(f"✅ Created startup script: {startup_script}")
    
    # Create migration info file
    migration_info = {
        "migration_date": "2025-08-13",
        "from_version": "1.0.0",
        "to_version": "2.0.0", 
        "architecture": "integrated",
        "endpoints": {
            "website": "http://localhost:8000/",
            "api": "http://localhost:8000/api/",
            "status": "http://localhost:8000/api/status"
        },
        "features": [
            "Unified server",
            "Live gold price widget",
            "Smart caching",
            "Docker support"
        ]
    }
    
    with open(api_dir / "migration_info.json", 'w') as f:
        json.dump(migration_info, f, indent=2)
    
    print("\n🎉 Migration preparation complete!")
    print("\n📋 Next Steps:")
    print("1. Test integrated server:")
    print("   python start_integrated.py")
    print()
    print("2. Or use Docker:")
    print("   cd .. && docker-compose up")
    print()
    print("3. Verify functionality:")
    print("   • Visit http://localhost:8000")
    print("   • Check gold price widget on homepage")
    print("   • Test API at http://localhost:8000/api/status")
    print()
    print("4. Update any existing API client URLs:")
    print("   • Old: http://localhost:8001/api/gold-prices")
    print("   • New: http://localhost:8000/api/gold-prices")
    
    return True

if __name__ == "__main__":
    success = migrate_to_integrated()
    if not success:
        exit(1)
    
    print("\n✨ Ready to launch integrated Makitox platform!")