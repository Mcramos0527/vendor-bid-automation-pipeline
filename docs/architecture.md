# Architecture Guide

## Pipeline Overview

The pipeline processes vendor bid reports through six stages:

1. **Email Monitoring** — Poll mailbox for vendor report attachments
2. **Status Filtering** — Keep only records with active agreement statuses
3. **Customer Classification** — Split named customers from "Various" (open channel)
4. **Region Mapping** — Map countries to ERP region codes via configurable matrices
5. **CSV Generation** — Transform to 38-column ERP format, split by REGIO+LIFNR
6. **Delivery** — Upload via SFTP, archive locally with date-stamped folders

## Delta Processing (v2.0)

Version 2.0 introduced an internal SQLite database to track known DPA numbers.
Instead of bulk-expiring all agreements every cycle, the engine compares incoming
data against the database and only processes changes — reducing ERP transactions by ~80%.

## File Splitting Logic

Output CSVs are split by the combination of REGIO (region code) and LIFNR (entity number).
Each unique combination gets its own file with a countered naming convention.
