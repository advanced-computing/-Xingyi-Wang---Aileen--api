from datetime import datetime

import pandas as pd
import pytest

DATA_URL = (
    "https://data.cityofnewyork.us/api/views/98wc-x49t/rows.csv?accessType=DOWNLOAD"
)


@pytest.fixture(scope="session")
def df():
    return pd.read_csv(DATA_URL)


def test_incident_date_not_future(df):
    """
    Data quality check:
    OCCUR_DATE should not be in the future.
    """
    dates = pd.to_datetime(df["OCCUR_DATE"], errors="coerce")
    today = pd.Timestamp(datetime.today().date())

    invalid_ratio = (dates > today).mean()
    assert invalid_ratio == 0


def test_lat_long_valid_range(df):
    """
    Data quality check:
    Latitude must be between -90 and 90.
    Longitude must be between -180 and 180.
    """
    lat = pd.to_numeric(df["Latitude"], errors="coerce")
    lon = pd.to_numeric(df["Longitude"], errors="coerce")

    mask = lat.notna() & lon.notna()

    valid_ratio = (lat[mask].between(-90, 90) & lon[mask].between(-180, 180)).mean()

    assert valid_ratio == 1.0


def test_borough_valid_values(df):
    """
    Data quality check:
    BORO should only contain NYC boroughs.
    At least 98% should be valid.
    """
    valid_boroughs = {"MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"}

    borough = df["BORO"].astype(str).str.upper().str.strip()

    valid_ratio = borough.isin(valid_boroughs).mean()

    assert valid_ratio >= 0.98
