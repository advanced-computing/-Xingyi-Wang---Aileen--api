-- Append loading method
-- Insert only new dates from the 2025 CPI vintage

INSERT INTO cpi_append
SELECT
    DATE AS date,
    PCPI25M2 AS cpi
FROM read_csv_auto('data/PCPI25M2.csv')
WHERE DATE NOT IN (
    SELECT date FROM cpi_append
);