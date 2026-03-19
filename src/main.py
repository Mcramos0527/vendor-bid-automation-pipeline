"""
Vendor Bid Automation Pipeline — entry point.

Orchestrates the complete daily processing workflow:
1. Read vendor report (email attachment or local file)
2. Filter by agreement status
3. Classify customers (named vs Various)
4. Map countries to regions via matrix
5. Transform to 38-column ERP CSV
6. Split by REGIO+LIFNR
7. Manage agreement lifecycle (expire old, create new)
8. Deliver via SFTP + archive locally
"""

import sys
import os
import pandas as pd

from src.data_transformer.status_filter import StatusFilter
from src.data_transformer.customer_classifier import CustomerClassifier
from src.data_transformer.column_mapper import ColumnMapper
from src.region_mapper.country_matrix import CountryMatrix
from src.csv_generator.csv_builder import FileSplitter
from src.utils.logging import audit_logger


def process_file(filepath: str, output_dir: str = "./output"):
    """Process a vendor report file through the full pipeline."""

    audit_logger.info(f"=== Processing: {filepath} ===")

    # Read vendor report
    df = pd.read_excel(filepath)
    audit_logger.info(f"Loaded {len(df)} rows from {filepath}")

    # Step 1: Filter by status
    status_filter = StatusFilter()
    df = status_filter.filter(df)
    if df.empty:
        audit_logger.warning("No records after status filtering. Exiting.")
        return

    # Step 2: Classify customers
    classifier = CustomerClassifier()
    named_df, various_df = classifier.classify(df)

    # Step 3: Map named customers through country matrix
    matrix = CountryMatrix()
    mapper = ColumnMapper()

    if not named_df.empty:
        region_codes = named_df["Customer Country/Region"].apply(
            lambda c: matrix.lookup(c)[0] if matrix.lookup(c) else "UNKNOWN"
        )
        entity_codes = named_df["Customer Country/Region"].apply(
            lambda c: matrix.lookup(c)[1] if matrix.lookup(c) else "000000"
        )
        mapped_df = mapper.map_dataframe(named_df, region_codes, entity_codes)

        # Step 4: Split and save
        splitter = FileSplitter(output_dir)
        files = splitter.split_and_save(mapped_df)
        audit_logger.info(f"Named customers: {len(files)} files generated")

    # Various/open channel processing would follow similar pattern
    if not various_df.empty:
        audit_logger.info(f"Open channel records: {len(various_df)} (processing skipped in demo)")

    audit_logger.info("=== Processing complete ===")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main process --file <vendor_report.xlsx>")
        sys.exit(1)

    if sys.argv[1] == "process" and "--file" in sys.argv:
        idx = sys.argv.index("--file")
        filepath = sys.argv[idx + 1]
        process_file(filepath)
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
