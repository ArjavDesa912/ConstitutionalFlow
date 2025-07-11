#!/usr/bin/env python3
"""
Example runner script for ConstitutionalFlow
This script runs the basic usage example to verify the system is working.
"""

import sys
import subprocess
import time
from pathlib import Path

def check_system_health():
    """Check if the system is running and healthy."""
    print("🔍 Checking system health...")
    
    try:
        import httpx
        import asyncio
        
        async def health_check():
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.get("http://localhost:8000/health")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ System is healthy: {data['status']}")
                        return True
                    else:
                        print(f"❌ Health check failed: {response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ Cannot connect to system: {e}")
                    return False
        
        return asyncio.run(health_check())
    except ImportError:
        print("❌ httpx not available. Install with: pip install httpx")
        return False

def start_system():
    """Start the ConstitutionalFlow system."""
    print("🚀 Starting ConstitutionalFlow system...")
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is available")
        
        # Start with Docker Compose
        print("🐳 Starting services with Docker Compose...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        # Wait for services to be ready
        print("⏳ Waiting for services to be ready...")
        time.sleep(15)
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not available, trying direct startup...")
        
        # Try to start the application directly
        try:
            print("🐍 Starting Python application...")
            subprocess.Popen([
                sys.executable, "-m", "uvicorn", "src.main:app", 
                "--host", "0.0.0.0", "--port", "8000"
            ])
            
            # Wait for startup
            time.sleep(10)
            return True
        except Exception as e:
            print(f"❌ Failed to start application: {e}")
            return False

def run_example():
    """Run the basic usage example."""
    print("🎯 Running ConstitutionalFlow example...")
    
    try:
        # Run the example script
        result = subprocess.run([
            sys.executable, "examples/basic_usage.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Example completed successfully!")
            print("\n📋 Example output:")
            print(result.stdout)
        else:
            print("❌ Example failed!")
            print("Error output:")
            print(result.stderr)
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to run example: {e}")
        return False

def main():
    """Main function to run the example."""
    print("🎉 ConstitutionalFlow Example Runner")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Please run this script from the ConstitutionalFlow root directory")
        return False
    
    # Check system health first
    if not check_system_health():
        print("\n🔄 System not running, attempting to start...")
        if not start_system():
            print("❌ Failed to start system")
            print("\n📋 Manual startup instructions:")
            print("1. Run: python scripts/setup.py")
            print("2. Run: uvicorn src.main:app --reload")
            print("3. Then run: python scripts/run_example.py")
            return False
        
        # Wait a bit more and check again
        time.sleep(5)
        if not check_system_health():
            print("❌ System still not healthy after startup")
            return False
    
    # Run the example
    print("\n🎯 Running example...")
    success = run_example()
    
    if success:
        print("\n🎉 Example completed successfully!")
        print("📚 Next steps:")
        print("- Check the API documentation at http://localhost:8000/docs")
        print("- Run tests with: python scripts/run_tests.py")
        print("- Explore the codebase in the src/ directory")
    else:
        print("\n❌ Example failed!")
        print("📋 Troubleshooting:")
        print("- Check if all services are running")
        print("- Review the logs for errors")
        print("- Run tests to verify functionality")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 