# Lab 8 – Data Warehousing with DuckDB (Simplified Version)

## Overview

This lab demonstrates three common data loading strategies used in data warehousing:

- append
- truncate and reload
- incremental update

We maintain a CPI (Consumer Price Index) database using DuckDB.

Two CPI vintage files are used:

- **PCPI24M1.csv** – CPI data available in January 2024
- **PCPI25M2.csv** – CPI data available in February 2025

The second file includes:

- new observations
- historical revisions

---

# Database Initialization

The database was initialized using **PCPI24M1.csv**.

The database contains three tables:

cpi_append
cpi_trunc
cpi_inc

Initially all three tables contain identical data.

Each table has two columns:

| column | description       |
| ------ | ----------------- |
| date   | observation month |
| cpi    | CPI value         |

---

# Running the Loading Scripts

Each script loads the updated CPI data from **PCPI25M2.csv**.

## Append method

Run:
duckdb cpi.duckdb < scripts/load_append.sql

### Expected result

- New dates from the 2025 vintage will be added.
- Existing rows will not be updated.

Therefore:
cpi_append

may contain outdated historical values if revisions occurred.

---

## Truncate method

Run:
duckdb cpi.duckdb < scripts/load_trunc.sql

### Expected result

The table will be fully reloaded with the newest CPI vintage.

cpi_trunc

will contain:

- new observations
- revised historical values

The table should match **PCPI25M2.csv** exactly.

---

## Incremental method

Run:
duckdb cpi.duckdb < scripts/load_inc.sql

### Expected result

The table will:

- insert new observations
- update revised historical observations

The final table should match **PCPI25M2.csv**.

---

# Manual Testing Instructions

After running each script, check the tables.

### Check row counts

SELECT COUNT() FROM cpi_append;
SELECT COUNT() FROM cpi_trunc;
SELECT COUNT(\*) FROM cpi_inc;

### Inspect recent rows

SELECT _ FROM cpi_append ORDER BY date DESC LIMIT 10;
SELECT _ FROM cpi_trunc ORDER BY date DESC LIMIT 10;
SELECT \* FROM cpi_inc ORDER BY date DESC LIMIT 10;

### Compare tables

SELECT _
FROM cpi_append
EXCEPT
SELECT _
FROM cpi_trunc;

This query helps detect rows that differ due to revisions.

---

# Discussion: Differences Between the Methods

### Append

Append inserts only new rows and does not update existing data.

Advantages:

- simple
- fast

Disadvantages:

- does not handle historical revisions

---

### Truncate and reload

This method deletes all rows and reloads the full dataset.

Advantages:

- always consistent with the newest data

Disadvantages:

- inefficient for large datasets

---

### Incremental loading

Incremental loading updates revised rows and inserts new rows.

Advantages:

- efficient
- maintains correct historical values

Disadvantages:

- more complex logic

---

# Conclusion

Append loading is fast but may produce outdated historical data.

Truncate-and-reload ensures correctness but is inefficient.

Incremental loading provides both correctness and efficiency, making it the preferred approach for production data pipelines.
