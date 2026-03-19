"""
CSV generator — builds ERP-compatible CSVs and splits by region/entity.
"""

import os
import pandas as pd
from typing import Dict, List
from datetime import datetime

from src.data_transformer.column_mapper import ERP_COLUMNS
from src.utils.naming import generate_csv_filename
from src.utils.logging import audit_logger


class CSVBuilder:
    """
    Builds ERP-compatible CSV files from mapped data.

    The CSV uses '~' as separator (not comma) to match
    the ERP system's expected input format.
    """

    SEPARATOR = "~"

    def build(self, df: pd.DataFrame) -> str:
        """Build CSV content string from mapped dataframe."""
        lines = []
        for _, row in df.iterrows():
            line = self.SEPARATOR.join(str(row.get(col, "")) for col in ERP_COLUMNS)
            lines.append(line)
        return "\n".join(lines)

    def save(self, df: pd.DataFrame, filepath: str) -> str:
        """Save CSV to file and return the filepath."""
        content = self.build(df)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        audit_logger.info(f"CSV saved: {filepath} ({len(df)} records)")
        return filepath


class FileSplitter:
    """
    Splits mapped data into separate CSVs by REGIO+LIFNR combination.

    Output naming convention:
        BPA2_VENDOR_{LIFNR}({counter})_{YYYYMMDD}.csv

    Each unique REGIO+LIFNR combination gets its own file.
    If the same LIFNR appears with different REGIOs, a counter
    is appended to the filename.
    """

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        self.csv_builder = CSVBuilder()

    def split_and_save(self, df: pd.DataFrame) -> List[str]:
        """
        Split dataframe by REGIO+LIFNR and save individual CSVs.

        Args:
            df: Mapped dataframe with REGIO and LIFNR columns.

        Returns:
            List of generated file paths.
        """
        if df.empty:
            audit_logger.warning("No data to split")
            return []

        # Group by REGIO + LIFNR
        groups = df.groupby(["REGIO", "LIFNR"])
        generated_files = []
        lifnr_counters: Dict[str, int] = {}

        for (regio, lifnr), group_df in groups:
            # Track counter per LIFNR
            lifnr_counters[lifnr] = lifnr_counters.get(lifnr, 0) + 1
            counter = lifnr_counters[lifnr]

            filename = generate_csv_filename(lifnr, counter)
            filepath = os.path.join(self.output_dir, filename)

            self.csv_builder.save(group_df, filepath)
            generated_files.append(filepath)

            audit_logger.info(
                f"Split: REGIO={regio}, LIFNR={lifnr} → {filename} "
                f"({len(group_df)} records)"
            )

        audit_logger.info(
            f"File splitting complete: {len(generated_files)} files generated"
        )
        return generated_files
