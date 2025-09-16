#!/usr/bin/env python3
"""
Setup Script for Contract Management AI System

This script helps users set up the environment, install dependencies,
and configure the system for first-time use.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        logging.error(f"Python {required_version[0]}.{required_version[1]}+ is required. Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install required Python packages"""
    try:
        logging.info("Installing dependencies from requirements.txt...")
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Install using pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            os.path.join(project_root, "requirements.txt")
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"Failed to install dependencies: {result.stderr}")
            return False
        
        logging.info("Dependencies installed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"Error installing dependencies: {str(e)}")
        return False

def setup_environment():
    """Set up environment variables and directory structure"""
    try:
        project_root = Path(__file__).parent.parent
        
        # Create necessary directories
        directories = [
            "data/sample_documents",
            "logs",
            "data/chroma_db"
        ]
        
        for directory in directories:
            dir_path = os.path.join(project_root, directory)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Created directory: {directory}")
        
        # Check if .env file exists, if not create from .env.example
        env_example = os.path.join(project_root, ".env.example")
        env_file = os.path.join(project_root, ".env")
        
        if not os.path.exists(env_file) and os.path.exists(env_example):
            shutil.copyfile(env_example, env_file)
            logging.info("Created .env file from .env.example")
            print("\nPlease update the .env file with your actual configuration:")
            print("1. Add your OpenAI API key")
            print("2. Configure email settings for reports")
            print("3. Set any other environment-specific variables")
        
        return True
        
    except Exception as e:
        logging.error(f"Error setting up environment: {str(e)}")
        return False

def check_openai_key():
    """Check if OpenAI API key is configured"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            logging.warning("OpenAI API key not configured or using placeholder value")
            print("\n⚠️  WARNING: OpenAI API key not properly configured.")
            print("Please update the OPENAI_API_KEY in your .env file")
            return False
        return True
        
    except ImportError:
        logging.warning("python-dotenv not installed, skipping environment check")
        return True

def create_sample_documents():
    """Create sample contract documents if they don't exist"""
    try:
        sample_dir = os.path.join(Path(__file__).parent.parent, "data", "sample_documents")
        
        # Sample content for demonstration
        sample_content = {
            "contract1.txt": "SAMPLE CONTRACT 1\nParties: Company A and Vendor B\nEffective Date: 2023-01-01\nExpiration Date: 2024-01-01\nAddress: 123 Main St, City, State",
            "contract2.txt": "SAMPLE CONTRACT 2\nParties: Company A and Supplier C\nEffective Date: 2023-06-01\nExpiration Date: 2024-06-01\nAddress: 456 Oak Ave, City, State",
            "contract3.txt": "SAMPLE CONTRACT 3\nParties: Company A and Partner D\nEffective Date: 2023-03-15\nExpiration Date: 2024-03-15\nAddress: 123 Main St, City, State"
        }
        
        for filename, content in sample_content.items():
            filepath = os.path.join(sample_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(content)
                logging.info(f"Created sample document: {filename}")
        
        return True
        
    except Exception as e:
        logging.error(f"Error creating sample documents: {str(e)}")
        return False

def show_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*60)
    print("SETUP COMPLETE - NEXT STEPS:")
    print("="*60)
    print("1. Add your contract documents to data/sample_documents/")
    print("2. Update .env file with your actual configuration:")
    print("   - OPENAI_API_KEY=your_actual_openai_api_key")
    print("   - Email settings for reports")
    print("3. Process documents: python -m src.document_processor")
    print("4. Run the application: streamlit run app/main.py")
    print("5. Schedule daily runs:")
    print("   - Linux/Mac: Add to crontab: 0 9 * * * /path/to/scripts/daily_run.py")
    print("   - Windows: Use Task Scheduler")
    print("="*60)

def main():
    """Main setup function"""
    print("Contract Management AI System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        logging.error("Dependency installation failed")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        logging.error("Environment setup failed")
        sys.exit(1)
    
    # Create sample documents
    create_sample_documents()
    
    # Check OpenAI key (non-critical)
    check_openai_key()
    
    # Show next steps
    show_next_steps()
    
    print("\nSetup completed successfully! 🎉")
    print("You can now proceed to configure and run the system.")

if __name__ == "__main__":
    main()
