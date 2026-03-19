"""Tests for status filter, customer classifier, column mapper, region mapper, CSV generator, and delta expiration."""

import pytest
import pandas as pd
import os
import tempfile

from src.data_transformer.status_filter import StatusFilter
from src.data_transformer.customer_classifier import CustomerClassifier
from src.data_transformer.column_mapper import ColumnMapper, ERP_COLUMNS, HARDCODED_VALUES
from src.region_mapper.country_matrix import CountryMatrix
from src.region_mapper.open_channel_matrix import OpenChannelMatrix
from src.csv_generator.csv_builder import CSVBuilder, FileSplitter
from src.expiration_engine.delta_expiration import DeltaExpirationEngine
from src.database.dpa_store import DPAStore
from src.utils.naming import generate_csv_filename


# === Status Filter ===

class TestStatusFilter:
    def test_filter_active_statuses(self):
        df = pd.DataFrame({
            "Status": [
                "DPA Open - Created In SAP",
                "DPA Open - Update Created In SAP",
                "DPA Closed",
                "DPA Expired",
            ],
            "DPA Number": ["D001", "D002", "D003", "D004"],
        })
        f = StatusFilter()
        result = f.filter(df)
        assert len(result) == 2
        assert set(result["DPA Number"]) == {"D001", "D002"}

    def test_filter_empty_dataframe(self):
        df = pd.DataFrame({"Status": [], "DPA Number": []})
        f = StatusFilter()
        assert len(f.filter(df)) == 0

    def test_missing_column(self):
        df = pd.DataFrame({"Wrong": ["x"]})
        f = StatusFilter()
        assert len(f.filter(df)) == 0


# === Customer Classifier ===

class TestCustomerClassifier:
    def test_classify_named_and_various(self):
        df = pd.DataFrame({
            "Customer Name": ["ACME Corp", "Various", "Beta Inc", "Various"],
        })
        classifier = CustomerClassifier()
        named, various = classifier.classify(df)
        assert len(named) == 2
        assert len(various) == 2

    def test_all_named(self):
        df = pd.DataFrame({"Customer Name": ["A", "B", "C"]})
        named, various = CustomerClassifier().classify(df)
        assert len(named) == 3
        assert len(various) == 0

    def test_case_insensitive(self):
        df = pd.DataFrame({"Customer Name": ["various", "VARIOUS", "VaRiOuS"]})
        _, various = CustomerClassifier().classify(df)
        assert len(various) == 3


# === Column Mapper ===

class TestColumnMapper:
    def test_map_row_hardcoded_values(self):
        mapper = ColumnMapper()
        vendor_row = {
            "DPA Number": "DPA-001",
            "End Customer Name": "ACME Corp",
            "DPA Valid From": "2024-01-01",
            "DPA Expiry Date": "2024-12-31",
            "Product Forecast ID": "PROD-001",
            "Approved Quantity": 100,
            "Approved Price": 49.99,
            "Customer Name": "ACME Corp",
        }
        result = mapper.map_row(vendor_row, "R040", "512068")
        assert result["ACURR"] == "USD"
        assert result["CONVE"] == "ZV06"
        assert result["CONCU"] == "ZC10"
        assert result["RSCHR"] == "C"
        assert result["REGIO"] == "R040"
        assert result["LIFNR"] == "512068"
        assert result["OPGAN"] == "DPA-001"

    def test_price_duplicated_to_valcu(self):
        mapper = ColumnMapper()
        result = mapper.map_row({"Approved Price": 99.99}, "R040", "512068")
        assert result["VALVE"] == "99.99"
        assert result["VALCU"] == "99.99"

    def test_38_columns_present(self):
        mapper = ColumnMapper()
        result = mapper.map_row({}, "R040", "512068")
        assert len(result) == len(ERP_COLUMNS)


# === Country Matrix ===

class TestCountryMatrix:
    @pytest.fixture
    def matrix(self):
        return CountryMatrix()

    @pytest.mark.parametrize("country,expected_region", [
        ("Spain", "R040"), ("Portugal", "R041"), ("Italy", "R042"),
        ("Germany", "R033"), ("France", "R043"), ("United Kingdom", "R0E5"),
        ("Ireland", "R0E5"), ("Austria", "R010"), ("Switzerland", "R011"),
        ("Sweden", "R022"), ("Denmark", "R023"), ("Norway", "R024"),
        ("Finland", "R019"), ("Netherlands", "R018"),
        ("Czech Republic", "R044"), ("Slovakia", "R048"),
        ("Hungary", "R027"), ("Romania", "R039"),
    ])
    def test_standard_country_mappings(self, matrix, country, expected_region):
        result = matrix.lookup(country)
        assert result is not None
        assert result[0] == expected_region

    def test_poland_special_entity(self, matrix):
        result = matrix.lookup("Poland")
        assert result == ("R026", "999299")

    def test_unknown_country(self, matrix):
        assert matrix.lookup("Narnia") is None

    def test_belgium_has_two_entries(self, matrix):
        all_entries = matrix.lookup_all("Belgium")
        assert len(all_entries) == 2

    def test_country_count(self, matrix):
        assert matrix.country_count >= 19


# === Open Channel Matrix ===

class TestOpenChannelMatrix:
    def test_combinations_loaded(self):
        m = OpenChannelMatrix()
        combos = m.get_all_combinations()
        assert len(combos) >= 5


# === CSV Builder ===

class TestCSVBuilder:
    def test_build_uses_tilde_separator(self):
        df = pd.DataFrame([{col: f"val_{col}" for col in ERP_COLUMNS}])
        builder = CSVBuilder()
        content = builder.build(df)
        assert "~" in content
        assert content.count("~") == len(ERP_COLUMNS) - 1

    def test_save_creates_file(self):
        df = pd.DataFrame([{col: "" for col in ERP_COLUMNS}])
        builder = CSVBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.csv")
            builder.save(df, path)
            assert os.path.exists(path)


# === File Splitter ===

class TestFileSplitter:
    def test_split_by_region_lifnr(self):
        data = [
            {**{c: "" for c in ERP_COLUMNS}, "REGIO": "R040", "LIFNR": "512068"},
            {**{c: "" for c in ERP_COLUMNS}, "REGIO": "R040", "LIFNR": "512068"},
            {**{c: "" for c in ERP_COLUMNS}, "REGIO": "R033", "LIFNR": "512068"},
        ]
        df = pd.DataFrame(data)
        with tempfile.TemporaryDirectory() as tmpdir:
            splitter = FileSplitter(tmpdir)
            files = splitter.split_and_save(df)
            assert len(files) == 2  # Two unique REGIO+LIFNR combinations


# === Delta Expiration ===

class TestDeltaExpiration:
    def test_analyze_identifies_changes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = DPAStore(os.path.join(tmpdir, "test.db"))
            db.add("DPA-001")
            db.add("DPA-002")
            db.add("DPA-003")

            engine = DeltaExpirationEngine(db)
            incoming = {"DPA-002", "DPA-003", "DPA-004"}
            result = engine.analyze(incoming)

            assert "DPA-004" in result["to_create"]
            assert "DPA-002" in result["unchanged"] or "DPA-003" in result["unchanged"]


# === Naming ===

class TestNaming:
    def test_csv_filename_format(self):
        name = generate_csv_filename("512068", 1)
        assert name.startswith("BPA2_VENDOR_512068(1)_")
        assert name.endswith(".csv")
