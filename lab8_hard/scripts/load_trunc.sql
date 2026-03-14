DELETE FROM cpi_trunc;

INSERT INTO cpi_trunc (pull_date, obs_date, cpi)
SELECT
    rc.pull_date,
    ld.obs_date,
    ld.cpi
FROM latest_data ld
CROSS JOIN run_context rc;