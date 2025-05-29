#!/usr/bin/env python3
"""
Email Handler Module

This module handles all email-related operations including:
- Connecting to Gmail via IMAP
- Searching for unread emails
- Parsing email content
- Sending automatic replies
- Marking emails as read
"""
import imaplib
import email
import smtplib
import logging
from email.message import EmailMessage
from email.header import decode_header
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailHandler:
    """Handles all email operations for the Auto Email Responder."""
    
    def __init__(self, email_address, password):
        """
        Initialize the EmailHandler with email credentials.
        
        Args:
            email_address (str): Gmail address
            password (str): App-specific password for Gmail
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = 'imap.gmail.com'
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.urgent_keywords = ['urgent', 'help', 'asap', 'emergency', 'important']
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test IMAP and SMTP connections to verify credentials."""
        # Test IMAP connection
        try:
            imap = imaplib.IMAP4_SSL(self.imap_server)
            imap.login(self.email_address, self.password)
            imap.logout()
        except Exception as e:
            logger.error(f"IMAP connection test failed: {e}")
            raise ConnectionError(f"Failed to connect to IMAP server: {e}")
        
        # Test SMTP connection
        try:
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.email_address, self.password)
            smtp.quit()
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            raise ConnectionError(f"Failed to connect to SMTP server: {e}")
    
    def _connect_to_imap(self):
        """Connect to the IMAP server and select the inbox."""
        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.email_address, self.password)
        imap.select('INBOX')
        return imap
    
    def _connect_to_smtp(self):
        """Connect to the SMTP server for sending emails."""
        smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(self.email_address, self.password)
        return smtp
    
    def _parse_email(self, raw_email):
        """
        Parse the raw email data into a structured format.
        
        Args:
            raw_email: Raw email data from IMAP
            
        Returns:
            dict: Structured email data with sender, subject, and body
        """
        msg = email.message_from_bytes(raw_email)
        
        # Get sender
        sender = msg.get('From', '')
        
        # Get subject
        subject = msg.get('Subject', '')
        if subject:
            # Decode subject if needed
            decoded_chunks = decode_header(subject)
            subject = ''.join(
                chunk.decode(encoding or 'utf-8') if isinstance(chunk, bytes) else chunk
                for chunk, encoding in decoded_chunks
            )
        
        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content
                if content_type == "text/plain":
                    try:
                        body_part = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body += body_part.decode(charset)
                    except Exception as e:
                        logger.warning(f"Failed to decode email body part: {e}")
        else:
            # Not multipart, just get the payload
            try:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
            except Exception as e:
                logger.warning(f"Failed to decode email body: {e}")
        
        return {
            'sender': sender,
            'subject': subject,
            'body': body,
            'message_id': msg.get('Message-ID', '')
        }
    
    def _contains_urgent_keywords(self, text):
        """
        Check if the text contains any urgent keywords.
        
        Args:
            text (str): Text to check for keywords
            
        Returns:
            bool: True if any keyword is found, False otherwise
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.urgent_keywords)
    
    def _send_auto_reply(self, to_email, subject, original_subject):
        """
        Send an automatic reply to the given email address.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Subject of the original email
            original_subject (str): Original subject for the reply
        """
        # Create the email message
        msg = EmailMessage()
        msg['From'] = self.email_address
        msg['To'] = to_email
        msg['Subject'] = f"Re: {original_subject}"
        
        # Current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Email body
        body = f"""
Hello,

This is an automatic response to your email regarding "{subject}".

I have received your message marked as urgent and will address it as soon as possible.
Please note that this is an automated reply sent at {current_time}.

If your matter requires immediate attention, please contact me directly by phone.

Best regards,
Auto Email Responder
        """
        msg.set_content(body)
        
        # Send the email
        try:
            smtp = self._connect_to_smtp()
            smtp.send_message(msg)
            smtp.quit()
            logger.info(f"Auto-reply sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")
            return False
    
    def _mark_as_read(self, imap, email_id):
        """
        Mark an email as read.
        
        Args:
            imap: IMAP connection
            email_id: ID of the email to mark as read
        """
        try:
            imap.store(email_id, '+FLAGS', '\\Seen')
            logger.debug(f"Marked email {email_id} as read")
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
    
    def process_unread_emails(self):
        """
        Process all unread emails in the inbox.
        
        This method:
        1. Connects to the IMAP server
        2. Searches for unread emails
        3. Processes each email
        4. Sends auto-replies if needed
        5. Marks emails as read
        """
        try:
            imap = self._connect_to_imap()
            logger.debug("Connected to IMAP server")
            
            # Search for unread emails
            status, messages = imap.search(None, 'UNSEEN')
            
            if status != 'OK':
                logger.warning("Failed to search for unread emails")
                imap.logout()
                return
            
            # Get the list of email IDs
            email_ids = messages[0].split()
            
            if not email_ids:
                logger.info("No unread emails found")
                imap.logout()
                return
            
            logger.info(f"Found {len(email_ids)} unread email(s)")
            
            # Process each email
            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, data = imap.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        logger.warning(f"Failed to fetch email {email_id}")
                        continue
                    
                    # Parse the email
                    email_data = self._parse_email(data[0][1])
                    sender = email_data['sender']
                    subject = email_data['subject']
                    body = email_data['body']
                    
                    logger.info(f"Processing email from {sender} with subject: {subject}")
                    
                    # Check if the email contains urgent keywords
                    if self._contains_urgent_keywords(subject) or self._contains_urgent_keywords(body):
                        logger.info(f"Urgent keywords found in email from {sender}")
                        
                        # Extract email address from sender
                        from_email = sender
                        if '<' in sender and '>' in sender:
                            from_email = sender.split('<')[1].split('>')[0]
                        
                        # Send auto-reply
                        if self._send_auto_reply(from_email, subject, subject):
                            logger.info(f"Auto-reply sent to {from_email}")
                            # Log to console
                            print(f"Replied to: {sender} - Subject: {subject}")
                        else:
                            logger.warning(f"Failed to send auto-reply to {from_email}")
                    
                    # Mark the email as read
                    self._mark_as_read(imap, email_id)
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
            
            # Logout from IMAP
            imap.logout()
            logger.debug("Disconnected from IMAP server")
            
        except Exception as e:
            logger.error(f"Error during email processing: {e}")