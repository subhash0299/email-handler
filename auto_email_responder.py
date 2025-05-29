#!/usr/bin/env python3
"""
Auto Email Responder - Main script

This script initializes and runs the automatic email responder system.
"""
import os
import time
import logging

from email_handler import EmailHandler
from scheduler import setup_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_env():
    """Simple .env file loader"""
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def main():
    """Main function to initialize and run the email responder."""
    # Load environment variables
    load_env()
    
    # Check if required environment variables are set
    required_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD']
    for var in required_vars:
        if not os.environ.get(var):
            logger.error(f"Missing required environment variable: {var}")
            logger.error("Please set up your .env file with the required credentials.")
            return
    
    email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')
    
    # Initialize the email handler
    try:
        email_handler = EmailHandler(email_address, email_password)
        logger.info("Email handler initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize email handler: {e}")
        return
    
    # Set up the scheduler
    logger.info("Setting up scheduler to check emails every 10 minutes")
    setup_scheduler(email_handler)
    
    # Run once immediately
    try:
        email_handler.process_unread_emails()
    except Exception as e:
        logger.error(f"Error during initial email processing: {e}")
    
    # Keep the script running
    logger.info("Auto Email Responder is now running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Auto Email Responder stopped by user")

if __name__ == "__main__":
    print("Starting Auto Email Responder...")
    main()