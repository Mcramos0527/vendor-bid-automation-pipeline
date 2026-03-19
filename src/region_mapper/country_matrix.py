"""
Country-to-region mapping matrix.

Maps country names from the vendor report to ERP region codes
and entity numbers (LIFNR) using externalized YAML configuration.
"""

from typing import Optional, Tuple, Dict

from src.config.loader import ConfigLoader
from src.utils.logging import audit_logger


class CountryMatrix:
    """
    Maps vendor country names to ERP region codes and entity numbers.

    The matrix supports:
    - Standard country-to-region mapping (Matrix 1)
    - Multiple region codes per country (e.g., Belgium has two)
    - Different entity numbers per region
    """

    def __init__(self):
        self.config = ConfigLoader()
        self._matrix = self.config.get_country_matrix()

    def lookup(self, country: str) -> Optional[Tuple[str, str]]:
        """
        Look up region code and entity for a country.

        Args:
            country: Country name from the vendor report.

        Returns:
            Tuple of (region_code, entity_code) or None.
        """
        normalized = country.strip().lower()

        for entry in self._matrix:
            if entry["country"].lower() == normalized:
                region = entry["region"]
                entity = str(entry["lifnr"])
                audit_logger.debug(f"Matrix lookup: '{country}' → {region} / {entity}")
                return (region, entity)

        audit_logger.warning(f"Matrix lookup: '{country}' → NOT FOUND")
        return None

    def lookup_all(self, country: str) -> list:
        """
        Get ALL region/entity combinations for a country.

        Some countries map to multiple region codes (e.g., Belgium
        has both R012/512068 and 1200/999296).
        """
        normalized = country.strip().lower()
        matches = [
            (entry["region"], str(entry["lifnr"]))
            for entry in self._matrix
            if entry["country"].lower() == normalized
        ]
        return matches

    @property
    def supported_countries(self) -> list:
        return sorted(set(e["country"] for e in self._matrix))

    @property
    def country_count(self) -> int:
        return len(set(e["country"] for e in self._matrix))
