DROP TABLE IF EXISTS shootings;
DROP TABLE IF EXISTS users;

CREATE TABLE shootings AS
SELECT *
FROM read_csv_auto('data/NYPD_Shootings_20260213.csv', HEADER=TRUE);

CREATE TABLE users (
    username VARCHAR PRIMARY KEY,
    age INTEGER,
    country VARCHAR
);

INSERT INTO users VALUES
    ('alice', 24, 'USA'),
    ('bob', 31, 'Canada'),
    ('carla', 27, 'USA');