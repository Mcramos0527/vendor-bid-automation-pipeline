"""YAML configuration loader."""

import os
from typing import Dict, Any, List, Set
from functools import lru_cache
import yaml


class ConfigLoader:

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
        )

    @lru_cache(maxsize=None)
    def _load(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._defaults(filename)

    def _defaults(self, filename: str) -> Dict[str, Any]:
        defaults = {
            "settings.yaml": {
                "active_statuses": ["DPA Open - Created In SAP", "DPA Open - Update Created In SAP"],
                "schedule_times": ["05:30", "17:30"],
                "sftp_host": "sftp.example.com",
                "sftp_path": "/prod",
                "archive_base": "./archive",
            },
            "country_matrix.yaml": {"matrix": [
                {"country": "Spain", "region": "R040", "lifnr": 512068},
                {"country": "Portugal", "region": "R041", "lifnr": 512068},
                {"country": "Italy", "region": "R042", "lifnr": 512068},
                {"country": "Belgium", "region": "R012", "lifnr": 512068},
                {"country": "Netherlands", "region": "R018", "lifnr": 512068},
                {"country": "United Kingdom", "region": "R0E5", "lifnr": 512068},
                {"country": "Ireland", "region": "R0E5", "lifnr": 512068},
                {"country": "Germany", "region": "R033", "lifnr": 512068},
                {"country": "Austria", "region": "R010", "lifnr": 512068},
                {"country": "Switzerland", "region": "R011", "lifnr": 512068},
                {"country": "France", "region": "R043", "lifnr": 512068},
                {"country": "Finland", "region": "R019", "lifnr": 512068},
                {"country": "Sweden", "region": "R022", "lifnr": 512068},
                {"country": "Denmark", "region": "R023", "lifnr": 512068},
                {"country": "Norway", "region": "R024", "lifnr": 512068},
                {"country": "Romania", "region": "R039", "lifnr": 512068},
                {"country": "Czech Republic", "region": "R044", "lifnr": 512068},
                {"country": "Slovakia", "region": "R048", "lifnr": 512068},
                {"country": "Hungary", "region": "R027", "lifnr": 512068},
                {"country": "Poland", "region": "R026", "lifnr": 999299},
                {"country": "Belgium", "region": "1200", "lifnr": 999296},
            ]},
            "open_channel_matrix.yaml": {"matrix": [
                {"region": "5599", "lifnr": 512068},
                {"region": "1218", "lifnr": 999296},
                {"region": "4200", "lifnr": 999299},
                {"region": "2600", "lifnr": 999299},
                {"region": "4041", "lifnr": 999296},
            ]},
        }
        return defaults.get(filename, {})

    def get_active_statuses(self) -> List[str]:
        return self._load("settings.yaml").get("active_statuses", [])

    def get_country_matrix(self) -> List[Dict]:
        return self._load("country_matrix.yaml").get("matrix", [])

    def get_open_channel_matrix(self) -> List[Dict]:
        return self._load("open_channel_matrix.yaml").get("matrix", [])

    def get_settings(self) -> Dict[str, Any]:
        return self._load("settings.yaml")
