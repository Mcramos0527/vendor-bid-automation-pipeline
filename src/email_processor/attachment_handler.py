"""Attachment validation and extraction."""
import os
from src.utils.logging import audit_logger


class AttachmentHandler:
    """Validates and processes email attachments."""

    VALID_EXTENSIONS = {".xlsx", ".xls"}

    def validate(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            audit_logger.error(f"Attachment not found: {filepath}")
            return False
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.VALID_EXTENSIONS:
            audit_logger.error(f"Invalid extension: {ext}")
            return False
        return True
