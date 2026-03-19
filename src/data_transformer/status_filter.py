"""
Status filter for vendor bid records.

Filters incoming bid records by configurable agreement status values
to identify records that need to be created or updated in the ERP.
"""

import pandas as pd
from typing import List, Optional

from src.config.loader import ConfigLoader
from src.utils.logging import audit_logger


class StatusFilter:
    """
    Filters vendor bid records by agreement status.

    Only records matching the configured status values are passed
    through for processing. All other records are discarded.

    Default active statuses:
    - "DPA Open - Created In SAP"
    - "DPA Open - Update Created In SAP"
    """

    def __init__(self, status_column: str = "Status"):
        self.config = ConfigLoader()
        self.status_column = status_column
        self._active_statuses = self.config.get_active_statuses()

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter dataframe to only include rows with active statuses.

        Args:
            df: Raw vendor report dataframe.

        Returns:
            Filtered dataframe with only active-status records.
        """
        if self.status_column not in df.columns:
            audit_logger.error(
                f"Status column '{self.status_column}' not found. "
                f"Available columns: {list(df.columns)}"
            )
            return pd.DataFrame()

        before_count = len(df)
        filtered = df[df[self.status_column].isin(self._active_statuses)].copy()
        after_count = len(filtered)

        audit_logger.info(
            f"Status filter: {before_count} → {after_count} records "
            f"(filtered by {self._active_statuses})"
        )

        return filtered

    @property
    def active_statuses(self) -> List[str]:
        return list(self._active_statuses)
