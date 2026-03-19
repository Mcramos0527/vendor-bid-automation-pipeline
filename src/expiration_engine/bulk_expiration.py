"""
Bulk expiration engine (v1 — legacy).

Expires ALL existing agreements before creating new ones.
Replaced by delta_expiration.py in v2.0 but kept for reference.
"""

from typing import List
from src.utils.logging import audit_logger


class BulkExpirationEngine:
    """
    Legacy bulk expiration — expires all UAN agreements then recreates.

    This approach was replaced by DeltaExpirationEngine because
    it wasted ~80% of ERP transactions on unchanged records.
    """

    def expire_all(self, variant: str = "VendorBS") -> List[str]:
        """
        Simulate bulk expiration of all UANs in a given ERP variant.

        In production, this interacts with the ERP transaction
        to select all, extract, and expire agreements.

        Args:
            variant: ERP variant name for filtering.

        Returns:
            List of expired UAN identifiers.
        """
        audit_logger.warning(
            "LEGACY: Bulk expiration triggered. "
            "Consider using DeltaExpirationEngine for efficiency."
        )

        # In production: ERP interaction
        # 1. Open transaction /nZO_SD_LIST with variant
        # 2. Select all UANs
        # 3. Extract to Excel and save as backup
        # 4. Expire all approvals
        # 5. Return list of expired UANs

        return []  # Placeholder — production has ERP automation
