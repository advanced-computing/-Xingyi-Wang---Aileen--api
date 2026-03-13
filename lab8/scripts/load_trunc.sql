-- Truncate and reload method

DELETE FROM cpi_trunc;

INSERT INTO cpi_trunc
SELECT
    DATE AS date,
    PCPI25M2 AS cpi
FROM read_csv_auto('data/PCPI25M2.csv');