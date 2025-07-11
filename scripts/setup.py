#!/usr/bin/env python3
"""
Setup script for ConstitutionalFlow
This script helps users configure the environment and initialize the system.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_content = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/constitutional_flow
REDIS_URL=redis://localhost:6379

# API Keys (Add your actual API keys here)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
COHERE_API_KEY=your-cohere-api-key-here

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# API Rate Limits (requests per minute)
OPENAI_RATE_LIMIT=100
ANTHROPIC_RATE_LIMIT=100
COHERE_RATE_LIMIT=100

# Cost Control (USD)
DAILY_BUDGET_LIMIT=100.0
MONTHLY_BUDGET_LIMIT=1000.0

# Performance Settings
MAX_CONCURRENT_TASKS=1000
TASK_TIMEOUT_SECONDS=300

# Logging
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping creation.")
        return
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("📝 Please edit .env file with your actual API keys and configuration")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker to use the full setup.")
        return False

def start_services():
    """Start database and Redis services using Docker Compose"""
    if not check_docker():
        return False
    
    print("🐳 Starting database and Redis services...")
    try:
        subprocess.run(["docker-compose", "up", "-d", "postgres", "redis"], check=True)
        print("✅ Services started successfully")
        print("⏳ Waiting for services to be ready...")
        import time
        time.sleep(10)  # Give services time to start
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("🗄️  Setting up database...")
    try:
        # Import and run database setup
        sys.path.append(str(Path(__file__).parent.parent))
        from src.core.database import create_tables
        create_tables()
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Welcome to ConstitutionalFlow Setup!")
    print("=" * 50)
    
    # Create environment file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Start services
    if not start_services():
        print("⚠️  Skipping service startup (Docker not available)")
    
    # Setup database
    if not run_migrations():
        print("❌ Setup failed at database setup")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: uvicorn src.main:app --reload")
    print("3. Visit: http://localhost:8000/docs")
    print("\n📚 For more information, see the README.md file")

if __name__ == "__main__":
    main() 