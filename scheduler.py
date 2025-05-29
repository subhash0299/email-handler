#!/usr/bin/env python3
"""
Scheduler Module

This module handles the scheduling of email checking at regular intervals.
"""
import schedule
import time
import logging
import threading

logger = logging.getLogger(__name__)

def setup_scheduler(email_handler):
    """
    Set up a scheduler to check emails at regular intervals.
    
    Args:
        email_handler: EmailHandler instance to process emails
    """
    def run_threaded(job_func):
        """Run the job function in a separate thread."""
        job_thread = threading.Thread(target=job_func)
        job_thread.daemon = True
        job_thread.start()
    
    def check_emails():
        """Function to check emails that will be scheduled."""
        logger.info("Scheduled check: Checking for new emails...")
        try:
            email_handler.process_unread_emails()
        except Exception as e:
            logger.error(f"Error during scheduled email check: {e}")
    
    # Schedule the job to run every 10 minutes
    schedule.every(10).minutes.do(run_threaded, check_emails)
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Scheduler started. Emails will be checked every 10 minutes.")

def run_scheduler():
    """Run the scheduler continuously."""
    while True:
        schedule.run_pending()
        time.sleep(1)