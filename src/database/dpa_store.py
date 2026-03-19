"""
DPA tracking database.

Maintains an internal record of all active DPA (Direct Product Agreement)
numbers for delta comparison between processing cycles.
"""

import sqlite3
from typing import Set
from datetime import date, datetime

from src.utils.logging import audit_logger


class DPAStore:
    """
    SQLite-backed store for tracking active DPA numbers.

    Used by the delta expiration engine to compare incoming
    vendor data against known agreements.
    """

    def __init__(self, db_path: str = "./data/dpa_store.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dpas (
                dpa_number TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add(self, dpa_number: str):
        """Add a DPA to the tracking database."""
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO dpas (dpa_number, created_at, last_seen) VALUES (?, ?, ?)",
            (dpa_number, now, now),
        )
        conn.commit()
        conn.close()

    def remove(self, dpa_number: str):
        """Remove a DPA from the tracking database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM dpas WHERE dpa_number = ?", (dpa_number,))
        conn.commit()
        conn.close()

    def get_all_dpa_numbers(self) -> Set[str]:
        """Get all DPA numbers in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT dpa_number FROM dpas")
        results = {row[0] for row in cursor.fetchall()}
        conn.close()
        return results

    def get_dpas_changed_since(self, dpa_numbers: Set[str], since_date: date) -> Set[str]:
        """Get DPAs from the given set that were last seen before the given date."""
        conn = sqlite3.connect(self.db_path)
        placeholders = ",".join("?" * len(dpa_numbers))
        cursor = conn.execute(
            f"SELECT dpa_number FROM dpas WHERE dpa_number IN ({placeholders}) "
            f"AND last_seen < ?",
            list(dpa_numbers) + [since_date.isoformat()],
        )
        results = {row[0] for row in cursor.fetchall()}
        conn.close()
        return results

    def update_last_seen(self, dpa_numbers: Set[str]):
        """Update the last_seen timestamp for a set of DPAs."""
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        for dpa in dpa_numbers:
            conn.execute(
                "UPDATE dpas SET last_seen = ? WHERE dpa_number = ?",
                (now, dpa),
            )
        conn.commit()
        conn.close()

    @property
    def count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM dpas")
        result = cursor.fetchone()[0]
        conn.close()
        return result
