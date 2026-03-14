CREATE TABLE IF NOT EXISTS cpi_append (
    pull_date DATE,
    obs_date DATE,
    cpi DOUBLE,
    PRIMARY KEY (pull_date, obs_date)
);

CREATE TABLE IF NOT EXISTS cpi_trunc (
    pull_date DATE,
    obs_date DATE,
    cpi DOUBLE
);

CREATE TABLE IF NOT EXISTS cpi_inc (
    obs_date DATE PRIMARY KEY,
    cpi DOUBLE,
    last_pull_date DATE
);