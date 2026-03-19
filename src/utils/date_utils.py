"""Date formatting utilities."""
from datetime import datetime, date


def is_first_execution_of_day(last_run: datetime = None) -> bool:
    if last_run is None:
        return True
    return last_run.date() < date.today()


def format_erp_date(d: str) -> str:
    """Convert various date formats to ERP-expected YYYYMMDD."""
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(str(d), fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    return str(d)
