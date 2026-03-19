"""File naming convention utilities."""

from datetime import datetime


def generate_csv_filename(lifnr: str, counter: int) -> str:
    """
    Generate CSV filename per the naming convention:
    BPA2_VENDOR_{LIFNR}({counter})_{YYYYMMDD}.csv
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    return f"BPA2_VENDOR_{lifnr}({counter})_{date_str}.csv"


def generate_expired_filename() -> str:
    """Generate filename for expired UAN export."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M")
    return f"RIE_expired_uan_{ts}.xls"


def generate_archive_folder() -> str:
    """Generate date-stamped archive folder name."""
    return datetime.utcnow().strftime("%Y%m%d")
