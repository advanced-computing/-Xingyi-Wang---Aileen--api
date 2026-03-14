UPDATE cpi_inc AS target
SET
    cpi = source.cpi,
    last_pull_date = source.last_pull_date
FROM (
    SELECT
        ld.obs_date,
        ld.cpi,
        rc.pull_date AS last_pull_date
    FROM latest_data ld
    CROSS JOIN run_context rc
) AS source
WHERE target.obs_date = source.obs_date
  AND target.cpi IS DISTINCT FROM source.cpi;

INSERT INTO cpi_inc (obs_date, cpi, last_pull_date)
SELECT
    source.obs_date,
    source.cpi,
    source.last_pull_date
FROM (
    SELECT
        ld.obs_date,
        ld.cpi,
        rc.pull_date AS last_pull_date
    FROM latest_data ld
    CROSS JOIN run_context rc
) AS source
LEFT JOIN cpi_inc target
    ON target.obs_date = source.obs_date
WHERE target.obs_date IS NULL;