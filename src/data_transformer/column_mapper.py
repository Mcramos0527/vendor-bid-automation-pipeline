"""
Column mapper for 38-column ERP CSV generation.

Maps vendor report columns to ERP-compatible output columns,
applying hardcoded values, blanks, and field transformations.
"""

import pandas as pd
from typing import Dict, Any, Optional

from src.config.loader import ConfigLoader
from src.utils.logging import audit_logger


# The 38 ERP columns in order
ERP_COLUMNS = [
    "OPGAN", "VERSI", "ATYPE", "REGIO", "DATAB", "DATBI", "BOOKF", "BOOKT",
    "ECUST", "ECAPT", "CATEG", "LIFNR", "ACURR", "VRATE", "EMAIL", "NOINT",
    "ALCHR", "ALKEY", "MFRPN", "MPNKH", "MAXQU", "MAXQC", "MINQC", "REMQU",
    "COMQU", "CONVE", "VALVE", "CONCU", "VALCU", "LVFRR", "LVLTO", "RSCHR",
    "RSKEY", "RSTXT", "STCEG", "SIGN", "ACCTM", "MCCOD", "SMAQU", "DEALID",
    "CMPLX",
]

# Vendor-to-ERP field mapping (vendor_column → erp_column)
FIELD_MAPPING = {
    "DPA Number": "OPGAN",
    "End Customer Name": "ECUST",
    "DPA Valid From": "DATAB",
    "DPA Expiry Date": "DATBI",
    "Product Forecast ID": "MFRPN",
    "Approved Quantity": "MAXQU",
    "Approved Price": "VALVE",
    "Customer Name": "RSTXT",
}

# Hardcoded values
HARDCODED_VALUES = {
    "ACURR": "USD",
    "CONVE": "ZV06",
    "CONCU": "ZC10",
    "RSCHR": "C",
}

# Columns where Approved Price is duplicated
PRICE_DUPLICATE_COLUMNS = ["VALVE", "VALCU"]


class ColumnMapper:
    """
    Maps vendor report columns to the 38-column ERP CSV format.

    Applies:
    - Direct field mappings (vendor column → ERP column)
    - Hardcoded values (ACURR="USD", CONVE="ZV06", etc.)
    - Region and entity codes from matrix lookup
    - Empty strings for unused columns
    - Price duplication to VALVE and VALCU
    """

    def __init__(self):
        self.config = ConfigLoader()

    def map_row(
        self,
        vendor_row: Dict[str, Any],
        region_code: str,
        entity_code: str,
    ) -> Dict[str, str]:
        """
        Map a single vendor row to the 38-column ERP format.

        Args:
            vendor_row: Dictionary of vendor report column values.
            region_code: Resolved region code from matrix lookup.
            entity_code: Resolved entity (LIFNR) from matrix lookup.

        Returns:
            Dictionary with all 38 ERP columns populated.
        """
        erp_row = {col: "" for col in ERP_COLUMNS}

        # Apply direct field mappings
        for vendor_col, erp_col in FIELD_MAPPING.items():
            if vendor_col in vendor_row:
                erp_row[erp_col] = str(vendor_row[vendor_col])

        # Apply hardcoded values
        for col, value in HARDCODED_VALUES.items():
            erp_row[col] = value

        # Apply region and entity
        erp_row["REGIO"] = region_code
        erp_row["LIFNR"] = entity_code

        # Duplicate price to VALCU
        if erp_row["VALVE"]:
            erp_row["VALCU"] = erp_row["VALVE"]

        return erp_row

    def map_dataframe(
        self,
        df: pd.DataFrame,
        region_codes: pd.Series,
        entity_codes: pd.Series,
    ) -> pd.DataFrame:
        """
        Map an entire vendor dataframe to ERP format.

        Args:
            df: Vendor report dataframe.
            region_codes: Series of region codes aligned with df index.
            entity_codes: Series of entity codes aligned with df index.

        Returns:
            DataFrame with 38 ERP columns.
        """
        rows = []
        for idx, vendor_row in df.iterrows():
            erp_row = self.map_row(
                vendor_row.to_dict(),
                region_code=region_codes.loc[idx],
                entity_code=entity_codes.loc[idx],
            )
            rows.append(erp_row)

        result = pd.DataFrame(rows, columns=ERP_COLUMNS)
        audit_logger.info(f"Column mapping: {len(result)} rows mapped to 38-column ERP format")
        return result
