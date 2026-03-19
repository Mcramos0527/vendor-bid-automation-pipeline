"""
Email mailbox monitor.

Polls a configured mailbox on schedule, identifies vendor reports
by subject pattern, and downloads attachments for processing.
"""
from typing import Optional
from src.utils.logging import audit_logger


class MailboxMonitor:
    """
    Monitors an email mailbox for vendor report attachments.

    Checks at configured intervals (5:30 and 17:30) for emails
    matching the expected subject pattern from the vendor.
    """

    def __init__(self, subject_pattern: str = "*VENDOR Report*"):
        self.subject_pattern = subject_pattern

    def check_for_report(self) -> Optional[str]:
        """
        Check mailbox for new vendor report email.

        Returns path to downloaded attachment, or None.
        In production: uses imaplib to connect to mailbox.
        """
        audit_logger.info(f"Checking mailbox for subject: {self.subject_pattern}")
        # Production: IMAP connection, search, download
        return None

    def download_attachment(self, email_id: str, output_dir: str) -> Optional[str]:
        """Download the Excel attachment from a vendor email."""
        audit_logger.info(f"Downloading attachment from email {email_id}")
        # Production: extract and save attachment
        return None
