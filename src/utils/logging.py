"""Audit logging."""
import logging
from collections import defaultdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class AuditLogger:
    def __init__(self, name="vendor-bid-pipeline"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        if not self._logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%Y-%m-%d %H:%M:%S"))
            self._logger.addHandler(h)

    def info(self, msg): self._logger.info(msg)
    def warning(self, msg): self._logger.warning(msg)
    def error(self, msg): self._logger.error(msg)
    def debug(self, msg): self._logger.debug(msg)


audit_logger = AuditLogger()
