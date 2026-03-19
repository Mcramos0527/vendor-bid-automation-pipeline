"""
Customer classifier.

Separates bid records into two processing streams:
1. Named customers — mapped through the standard country matrix
2. "Various" customers — mapped through the open channel matrix
"""

import pandas as pd
from typing import Tuple

from src.utils.logging import audit_logger


class CustomerClassifier:
    """
    Classifies bid records based on customer name.

    Records with "Various" as the customer name represent open channel
    bids and follow a different mapping matrix. All other records
    are named customers that use the standard country-to-region matrix.
    """

    VARIOUS_KEYWORD = "Various"

    def classify(self, df: pd.DataFrame, customer_column: str = "Customer Name") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split dataframe into named customers and open channel records.

        Args:
            df: Filtered vendor report dataframe.
            customer_column: Column containing the customer name.

        Returns:
            Tuple of (named_customers_df, various_df)
        """
        if customer_column not in df.columns:
            audit_logger.error(f"Customer column '{customer_column}' not found")
            return df, pd.DataFrame()

        # Split into named and Various
        is_various = df[customer_column].str.strip().str.lower() == self.VARIOUS_KEYWORD.lower()

        named_df = df[~is_various].copy()
        various_df = df[is_various].copy()

        audit_logger.info(
            f"Customer classification: {len(named_df)} named customers, "
            f"{len(various_df)} open channel (Various)"
        )

        return named_df, various_df
