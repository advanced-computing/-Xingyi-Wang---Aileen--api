Lab 8 – CPI Data Warehousing with DuckDB
Overview

This project simulates maintaining a CPI database when source data is continuously updated and historical values may be revised over time.

The CPI data used in this lab comes from the Philadelphia Federal Reserve. The dataset is organized in a wide vintage format, where:

Each row represents an observation month.

Each column represents a CPI vintage release (for example PCPI04M1, PCPI04M2, PCPI04M3).

Example structure of the dataset:

DATE PCPI04M1 PCPI04M2 PCPI04M3
2003:09 185.0 185.1 185.1
2003:10 185.0 184.9 184.9
2003:11 184.6 184.6 184.6
2003:12 185.0 184.9 184.9
2004:01 NA 185.8 185.8
2004:02 NA NA 186.3

Each CPI vintage is released monthly. Additionally, historical revisions are released every February. A revision released in year t may update values for years t-5 through t-1.

The goal of this project is to simulate maintaining a CPI database when revisions occur and to compare different data loading strategies.

Project Structure
lab8/
├── data/
│ └── pcpiMvMd.xlsx
├── scripts/
│ ├── init_db.sql
│ ├── load_append.sql
│ ├── load_trunc.sql
│ └── load_inc.sql
├── cpi.duckdb
└── README.md
Description of files
File Description
pcpiMvMd.xlsx CPI dataset containing all vintages
init_db.sql Initializes the database and defines helper functions
load_append.sql Implements append loading
load_trunc.sql Implements truncate-and-reload loading
load_inc.sql Implements incremental loading
cpi.duckdb Persistent DuckDB database
Database Initialization

The database is initialized using the script:

scripts/init_db.sql

This script performs the following steps:

Loads the CPI dataset from the Excel file.

Converts the wide vintage dataset into a long-format table.

Creates three target tables:

cpi_append

cpi_trunc

cpi_inc

Defines a function called get_latest_data(pull_date).

After initialization, the three tables exist but contain no data.

The get_latest_data Function

The function get_latest_data(pull_date) returns the most recent CPI data available as of a given pull date.

The function returns exactly two columns:

column description
date observation month
cpi CPI value

The function determines the latest available vintage release whose release date is less than or equal to the specified pull_date.

Example:

If the pull date is:

2004-01-15

the function should return CPI values from the vintage:

PCPI04M1

If the pull date is:

2004-02-15

the function should return CPI values from:

PCPI04M2

All other scripts in this project interact with the source dataset only through this function.
