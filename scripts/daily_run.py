#!/usr/bin/env python3
"""
Daily Run Script for Contract Management AI Agent

This script runs the daily monitoring and reporting functionality.
It can be scheduled with cron or Windows Task Scheduler.
"""

import os
import sys
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from document_processor import DocumentProcessor
from daily_agent import DailyAgent
from config import EMAIL_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'daily_run.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_daily_check():
    """Run the daily contract monitoring check"""
    try:
        logging.info("Starting daily contract monitoring run...")
        
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Load existing vector store
        vectorstore = processor.load_vectorstore()
        if vectorstore is None:
            logging.error("Vector store not found. Please process documents first.")
            return False
        
        # Initialize daily agent
        agent = DailyAgent(vectorstore, EMAIL_CONFIG)
        
        # Run daily check
        report = agent.run_daily_check()
        
        logging.info("Daily contract monitoring completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error during daily run: {str(e)}")
        return False

def main():
    """Main function for the daily run script"""
    print(f"Contract Management Daily Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success = run_daily_check()
    
    if success:
        print("Daily run completed successfully!")
        sys.exit(0)
    else:
        print("Daily run failed! Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
