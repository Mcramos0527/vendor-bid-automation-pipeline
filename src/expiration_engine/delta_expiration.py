"""
Delta expiration engine (v2.0).

Instead of bulk-expiring all agreements and recreating them,
this engine compares incoming data against an internal database
and only expires records that have been removed or changed.
"""

import pandas as pd
from typing import Set, List, Dict
from datetime import datetime, date

from src.database.dpa_store import DPAStore
from src.utils.logging import audit_logger


class DeltaExpirationEngine:
    """
    Intelligent delta-based expiration engine.

    Compares incoming vendor data with the internal DPA database to
    determine which agreements need to be expired and which are new.

    This replaced the bulk expiration approach (v1) which expired
    ALL agreements and recreated them every cycle — wasting ~80%
    of ERP transactions on unchanged records.
    """

    def __init__(self, db: DPAStore = None):
        self.db = db or DPAStore()

    def analyze(
        self,
        incoming_dpas: Set[str],
        is_first_execution: bool = False,
    ) -> Dict[str, List[str]]:
        """
        Compare incoming DPAs against the database and determine actions.

        Args:
            incoming_dpas: Set of DPA numbers from the new vendor report.
            is_first_execution: True if this is the first run of the day.

        Returns:
            Dictionary with 'to_expire', 'to_create', and 'unchanged' lists.
        """
        existing_dpas = self.db.get_all_dpa_numbers()

        # DPAs in database but NOT in new file → need to be expired
        to_expire = existing_dpas - incoming_dpas

        # DPAs in new file but NOT in database → need to be created
        to_create = incoming_dpas - existing_dpas

        # DPAs in both → unchanged, no action needed
        unchanged = incoming_dpas & existing_dpas

        # Apply date-based filtering for expiration
        if to_expire:
            to_expire = self._apply_date_filter(to_expire, is_first_execution)

        audit_logger.info(
            f"Delta analysis: {len(to_expire)} to expire, "
            f"{len(to_create)} to create, {len(unchanged)} unchanged"
        )

        return {
            "to_expire": sorted(to_expire),
            "to_create": sorted(to_create),
            "unchanged": sorted(unchanged),
        }

    def _apply_date_filter(
        self, dpas_to_expire: Set[str], is_first_execution: bool
    ) -> Set[str]:
        """
        Apply date-based filtering for expiration.

        Rules:
        - First execution of the day → filter by previous day's changes
        - Any other execution → filter by current day's changes
        """
        if is_first_execution:
            filter_date = date.today().replace(day=date.today().day - 1)
            audit_logger.info(f"First execution: filtering by yesterday ({filter_date})")
        else:
            filter_date = date.today()
            audit_logger.info(f"Subsequent execution: filtering by today ({filter_date})")

        filtered = self.db.get_dpas_changed_since(dpas_to_expire, filter_date)
        return filtered

    def update_database(self, incoming_dpas: Set[str], analysis: Dict[str, List[str]]):
        """
        Update the internal database after processing.

        - Remove expired DPAs
        - Add newly created DPAs
        """
        # Remove expired
        for dpa in analysis["to_expire"]:
            self.db.remove(dpa)

        # Add new
        for dpa in analysis["to_create"]:
            self.db.add(dpa)

        audit_logger.info(
            f"Database updated: {len(analysis['to_expire'])} removed, "
            f"{len(analysis['to_create'])} added"
        )
