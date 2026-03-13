-- Initialize CPI database using January 2024 vintage data

-- Create table for append method
CREATE TABLE cpi_append AS
SELECT
    DATE AS date,
    PCPI24M1 AS cpi
FROM read_csv_auto('data/PCPI24M1.csv');

-- Create table for truncate method
CREATE TABLE cpi_trunc AS
SELECT
    DATE AS date,
    PCPI24M1 AS cpi
FROM read_csv_auto('data/PCPI24M1.csv');

-- Create table for incremental method
CREATE TABLE cpi_inc AS
SELECT
    DATE AS date,
    PCPI24M1 AS cpi
FROM read_csv_auto('data/PCPI24M1.csv');