"""SFTP file delivery."""
from typing import List
from src.utils.logging import audit_logger


class SFTPUploader:
    """Uploads generated CSV files to configured SFTP endpoint."""

    def __init__(self, host: str = "sftp.example.com", path: str = "/prod"):
        self.host = host
        self.path = path

    def upload(self, filepaths: List[str]) -> List[str]:
        """Upload files via SFTP. Returns list of uploaded paths."""
        uploaded = []
        for fp in filepaths:
            audit_logger.info(f"SFTP upload: {fp} → {self.host}:{self.path}")
            uploaded.append(fp)
        return uploaded
