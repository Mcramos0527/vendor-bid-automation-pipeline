"""
Open channel mapping matrix.

Maps "Various" (open channel) bid records to their specific
region/entity combinations for ERP processing.
"""

from typing import List, Tuple

from src.config.loader import ConfigLoader
from src.utils.logging import audit_logger


class OpenChannelMatrix:
    """
    Maps open channel bids to region/entity combinations.

    Open channel bids (Customer Name = "Various") are replicated
    across multiple region/entity combinations as defined in
    the open channel matrix configuration.
    """

    def __init__(self):
        self.config = ConfigLoader()
        self._matrix = self.config.get_open_channel_matrix()

    def get_all_combinations(self) -> List[Tuple[str, str]]:
        """
        Get all region/entity combinations for open channel processing.

        Returns:
            List of (region_code, entity_code) tuples.
        """
        return [
            (entry["region"], str(entry["lifnr"]))
            for entry in self._matrix
        ]

    @property
    def combination_count(self) -> int:
        return len(self._matrix)
