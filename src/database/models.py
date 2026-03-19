"""Database models for DPA tracking."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DPARecord:
    dpa_number: str
    created_at: datetime
    last_seen: datetime
    status: str = "active"
