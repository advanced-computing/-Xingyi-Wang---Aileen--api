# NYPD Shootings Dataset (98wc-x49t) – Data Profiling Takeaways

Dataset: NYC Open Data – NYPD Shootings

## 1. Missingness in demographic fields (should be checked)
Victim and suspect demographic fields (e.g., age group, race, sex) contain missing or "UNKNOWN" values.
This matters because demographic analysis may be biased if missingness is high.

## 2. Date and time validity must be enforced
The incident date field must not contain future dates.
This matters because time-series analysis depends on valid chronological data.

## 3. Geographic coordinates must be valid
Latitude and Longitude fields exist and must fall within valid numeric ranges.
Invalid coordinates would break mapping and spatial analysis.

## 4. Borough values should be restricted to NYC boroughs
Borough should only contain: Manhattan, Brooklyn, Queens, Bronx, Staten Island.
Unexpected values indicate data entry or formatting issues.

## 5. Shooting incidents should have a unique identifier
Incident key / record ID appears to function as a primary key.
Duplicates would inflate incident counts and distort statistics.