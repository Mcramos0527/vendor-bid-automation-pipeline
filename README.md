# Vendor Bid Automation Pipeline

> End-to-end automation that processes daily vendor bid reports, transforms pricing data into ERP-compatible CSVs split by region, manages agreement lifecycles (create/expire), and delivers files via SFTP — replacing 36 hours/month of manual work.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Overview

**Vendor Bid Automation Pipeline** is a Python automation system that replaces a fully manual daily process for managing vendor pricing agreements across EMEA. It ingests vendor bid reports from email, transforms the data against region/entity mapping matrices, generates ERP-compatible CSV files split by region, manages agreement expiration in the ERP system, and delivers output files via SFTP.

### The Problem

Every day, a vendor sends a report containing hundreds of bid/pricing records for products across 20+ European countries. A team member had to:

1. Manually open the email attachment
2. Filter records by status
3. Look up each country in a mapping matrix to find the correct ERP region and entity codes
4. Transform 38+ columns into ERP-compatible CSV format with hardcoded values
5. Split the output into separate files per region/entity combination
6. Expire outdated agreements in the ERP system
7. Upload the new files via SFTP

**Time cost:** ~36 hours/month of repetitive manual work.

### The Solution

This pipeline automates the entire workflow:

```
Email Attachment → Filter by Status → Map Country to Region →
Transform to CSV → Split by Region/Entity → Expire Old Agreements →
Upload via SFTP → Archive + Audit Log
```

**Result:** Fully automated, runs twice daily (5:30 and 17:30), zero manual intervention, full traceability.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Email Processor                            │
│  Monitor mailbox → Download attachment → Filter status  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Data Transformer                           │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐   │
│  │ Status       │ │ Customer     │ │ Region/Entity  │   │
│  │ Filter       │ │ Classifier   │ │ Mapper         │   │
│  └──────────────┘ └──────────────┘ └────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              CSV Generator                              │
│  38-column ERP format → Split by REGIO+LIFNR → Name     │
└──────────────┬───────────────────┬──────────────────────┘
               │                   │
               ▼                   ▼
┌──────────────────────┐ ┌────────────────────────────────┐
│  Expiration Engine   │ │  SFTP Delivery + Archive       │
│  Expire old UAN/DPA  │ │  Upload + local backup         │
│  in ERP system       │ │  with date-stamped folders     │
└──────────────────────┘ └────────────────────────────────┘
```

---

## Key Features

- **Email Monitoring** — Polls a mailbox on schedule, identifies vendor reports by subject pattern, downloads attachments
- **Status Filtering** — Filters bid records by configurable status values (e.g., "Open - Created", "Open - Update Created")
- **Customer Classification** — Separates named customers from "Various" (open channel) records for different processing paths
- **Country-to-Region Matrix** — Maps 20+ countries to ERP region codes and entity numbers via YAML config
- **Open Channel Matrix** — Separate mapping for open channel (non-customer-specific) bids
- **38-Column CSV Transformation** — Maps vendor fields to ERP columns, applies hardcoded values, leaves blanks where required
- **Region-Based File Splitting** — Generates one CSV per unique REGIO+LIFNR combination with countered naming
- **Agreement Lifecycle Management** — Expires outdated agreements (UAN/DPA) in the ERP system before creating new ones
- **Delta Processing (v2.0)** — Compares incoming data against an internal database to expire only changed/removed records instead of bulk expiration
- **SFTP Delivery** — Uploads generated CSVs to a configured SFTP endpoint
- **Archival** — Saves copies to date-stamped local folders for audit trail
- **Scheduled Execution** — Runs at 5:30 and 17:30 daily, triggered by email arrival

---

## Data Flow

### Input: Vendor Report (Excel attachment)

| Column | Description |
|--------|-------------|
| DPA Number | Direct Product Agreement identifier |
| Status | Agreement status (filter criteria) |
| Customer Name | End customer or "Various" for open channel |
| Customer Country/Region | Country name for matrix lookup |
| End Customer Name | Customer display name for ERP |
| DPA Valid From | Agreement start date |
| DPA Expiry Date | Agreement end date |
| Product Forecast ID | Product identifier |
| Approved Quantity | Quantity under agreement |
| Approved Price | Price under agreement |

### Output: ERP-Compatible CSV (38 columns)

```
OPGAN~VERSI~ATYPE~REGIO~DATAB~DATBI~BOOKF~BOOKT~ECUST~ECAPT~CATEG~
LIFNR~ACURR~VRATE~EMAIL~NOINT~ALCHR~ALKEY~MFRPN~MPNKH~MAXQU~MAXQC~
MINQC~REMQU~COMQU~CONVE~VALVE~CONCU~VALCU~LVFRR~LVLTO~RSCHR~RSKEY~
RSTXT~STCEG~SIGN~ACCTM~MCCOD~SMAQU~DEALID~CMPLX
```

Key mappings:
- `OPGAN` ← DPA Number
- `REGIO` ← Country mapped through Matrix 1
- `LIFNR` ← Entity number from Matrix 1
- `ACURR` ← "USD" (hardcoded)
- `CONVE` ← "ZV06" (hardcoded)
- `CONCU` ← "ZC10" (hardcoded)
- `RSCHR` ← "C" (hardcoded)

---

## Country-to-Region Matrix

| Country | Region Code | Entity (LIFNR) |
|---------|-------------|-----------------|
| Spain | R040 | 512068 |
| Portugal | R041 | 512068 |
| Italy | R042 | 512068 |
| Belgium | R012 | 512068 |
| Netherlands | R018 | 512068 |
| United Kingdom | R0E5 | 512068 |
| Ireland | R0E5 | 512068 |
| Germany | R033 | 512068 |
| Austria | R010 | 512068 |
| Switzerland | R011 | 512068 |
| France | R043 | 512068 |
| Finland | R019 | 512068 |
| Sweden | R022 | 512068 |
| Denmark | R023 | 512068 |
| Norway | R024 | 512068 |
| Romania | R039 | 512068 |
| Czech Republic | R044 | 512068 |
| Slovakia | R048 | 512068 |
| Hungary | R027 | 512068 |
| Poland | R026 | 999299 |
| Belgium (alt) | R012-A | 999296 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Processing | pandas |
| Email | imaplib / email |
| File Transfer | paramiko (SFTP) |
| Database | SQLite |
| Configuration | YAML |
| Scheduling | APScheduler |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker |

---

## Quick Start

```bash
git clone https://github.com/Mcramos0527/vendor-bid-automation-pipeline.git
cd vendor-bid-automation-pipeline

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Process a sample vendor report
python -m src.main process --file sample_data/vendor_report_sample.xlsx

# Run tests
pytest tests/ -v --cov=src
```

---

## Project Structure

```
vendor-bid-automation-pipeline/
├── src/
│   ├── main.py                          # Entry point and scheduler
│   ├── email_processor/
│   │   ├── mailbox_monitor.py           # Email polling and attachment download
│   │   └── attachment_handler.py        # Attachment validation and extraction
│   ├── data_transformer/
│   │   ├── status_filter.py             # Filter by agreement status
│   │   ├── customer_classifier.py       # Named vs "Various" customer split
│   │   └── column_mapper.py             # 38-column vendor-to-ERP mapping
│   ├── region_mapper/
│   │   ├── country_matrix.py            # Country-to-region mapping engine
│   │   └── open_channel_matrix.py       # Open channel mapping engine
│   ├── expiration_engine/
│   │   ├── bulk_expiration.py           # v1: Expire all then recreate
│   │   └── delta_expiration.py          # v2: Compare and expire only changes
│   ├── csv_generator/
│   │   ├── csv_builder.py               # Build 38-column CSV records
│   │   ├── file_splitter.py             # Split by REGIO+LIFNR
│   │   └── sftp_uploader.py             # SFTP delivery
│   ├── database/
│   │   ├── dpa_store.py                 # DPA tracking database
│   │   └── models.py                    # Database models
│   ├── config/
│   │   ├── settings.py                  # Application settings
│   │   └── loader.py                    # YAML config loader
│   └── utils/
│       ├── date_utils.py                # Date formatting utilities
│       └── naming.py                    # File naming conventions
├── tests/
│   ├── test_status_filter.py
│   ├── test_customer_classifier.py
│   ├── test_column_mapper.py
│   ├── test_region_mapper.py
│   ├── test_csv_generator.py
│   ├── test_delta_expiration.py
│   └── test_integration.py
├── config/
│   ├── country_matrix.yaml
│   ├── open_channel_matrix.yaml
│   ├── column_mapping.yaml
│   └── settings.yaml
├── sample_data/
│   └── vendor_report_sample.xlsx
├── docs/
│   ├── architecture.md
│   └── column_mapping_reference.md
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── LICENSE
```

---

## Delta Processing (v2.0)

Version 2.0 introduced intelligent delta processing to avoid the inefficiency of bulk-expiring all agreements every cycle:

```
New Report → Compare with Internal DB →
  ├── Records in DB but NOT in new file → Expire in ERP
  ├── Records in new file but NOT in DB → Create new UAN
  └── Records in both → Skip (no action needed)
```

**Date-aware filtering:**
- First execution of the day (5:30) → filter by previous day's changes
- Second execution (17:30) → filter by current day's changes

This reduced ERP transaction volume by ~80% and eliminated unnecessary expiration/recreation cycles.

---

## Roadmap

- [x] Email monitoring and attachment download
- [x] Status-based record filtering
- [x] Named customer processing with Matrix 1
- [x] 38-column CSV transformation with hardcoded values
- [x] Region-based file splitting (REGIO+LIFNR)
- [x] SFTP upload with naming convention
- [x] Date-stamped archival
- [x] Bulk expiration engine (v1)
- [x] Delta processing with internal database (v2)
- [x] Open channel / "Various" customer processing
- [ ] Monitoring dashboard for processing statistics
- [ ] Slack/Teams notifications on processing completion
- [ ] Retry logic for SFTP failures

---

## Author

**Max Ramos** — Technical Business Analyst & Automation Engineer

- Enterprise systems integration specialist with 10+ years of experience
- Background in ERP environments, vendor data processing, and process automation
- [LinkedIn](https://www.linkedin.com/in/max-ramos-6a1942126) · [GitHub](https://github.com/Mcramos0527)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
