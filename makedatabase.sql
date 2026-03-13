-- Connect to a new or existing DuckDB database file
-- This creates the file if it doesn't exist
ATTACH DATABASE 'shooting.db' AS mydb;

-- Create table in this persistent database
CREATE TABLE mydb.shooting AS SELECT * FROM read_csv("data/NYPD_Shootings_20260213.csv");