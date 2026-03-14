INSERT INTO cpi_append (pull_date, obs_date, cpi)
SELECT
    rc.pull_date,
    ld.obs_date,
    ld.cpi
FROM latest_data ld
CROSS JOIN run_context rc
WHERE NOT EXISTS (
    SELECT 1
    FROM cpi_append a
    WHERE a.pull_date = rc.pull_date
      AND a.obs_date = ld.obs_date
);