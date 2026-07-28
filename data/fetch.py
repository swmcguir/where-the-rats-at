"""Chicago Data Portal API client for rodent complaint data."""

import os
import time

import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta
import streamlit as st

# Chicago Data Portal endpoints
CHICAGO_DATA_PORTAL = "data.cityofchicago.org"
DATASET_311_REQUESTS = "v6vf-nfxy"  # All 311 service requests
DATASET_WARD_OFFICES = "htai-wnw4"  # Alderman info

# Large pulls (a year is ~50k rows) routinely exceed sodapy's 10s default,
# especially on unauthenticated (throttled) requests
SOCRATA_TIMEOUT_SECONDS = 90
SOCRATA_ATTEMPTS = 3


def _get_app_token():
    """Optional Socrata app token - lifts the strict throttling on
    anonymous requests. Set SOCRATA_APP_TOKEN as an env var or in
    Streamlit secrets."""
    token = os.environ.get("SOCRATA_APP_TOKEN")
    if token:
        return token
    try:
        return st.secrets.get("SOCRATA_APP_TOKEN")
    except Exception:
        return None


def _socrata_get(dataset: str, **query):
    """Run a Socrata query with a generous timeout and retries.

    Raises on final failure so callers (and st.cache_data) never treat a
    transient outage as a valid result.
    """
    client = Socrata(CHICAGO_DATA_PORTAL, _get_app_token(),
                     timeout=SOCRATA_TIMEOUT_SECONDS)
    last_error = None
    for attempt in range(SOCRATA_ATTEMPTS):
        try:
            return client.get(dataset, **query)
        except Exception as e:
            last_error = e
            if attempt < SOCRATA_ATTEMPTS - 1:
                time.sleep(2 ** attempt)
    raise last_error


# NOTE: this raises on failure. st.cache_data does not cache exceptions,
# so an outage never poisons the cache - the next rerun retries. The public
# fetch_rodent_complaints wrapper converts failures to an empty DataFrame.
@st.cache_data(ttl=3600)  # Cache for 1 hour
def _fetch_rodent_complaints_cached(days_back: int) -> pd.DataFrame:
    # Calculate date range
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    # Query for rodent baiting complaints using SoQL (Socrata Query Language)
    results = _socrata_get(
        DATASET_311_REQUESTS,
        where=f"sr_type = 'Rodent Baiting/Rat Complaint' AND created_date >= '{start_date}'",
        select="sr_number, sr_type, created_date, closed_date, status, "
               "street_address, street_name, street_direction, street_type, "
               "ward, community_area, zip_code, latitude, longitude",
        limit=500000,  # Get up to 500k records
        order="created_date DESC"
    )

    df = pd.DataFrame.from_records(results)

    if df.empty:
        return df

    # Socrata omits a column entirely if it is null for every returned record,
    # so guarantee the schema pages rely on
    expected_columns = [
        'sr_number', 'sr_type', 'created_date', 'closed_date', 'status',
        'street_address', 'street_name', 'street_direction', 'street_type',
        'ward', 'community_area', 'zip_code', 'latitude', 'longitude'
    ]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    # Convert data types
    df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
    df = df.dropna(subset=['created_date'])
    df['closed_date'] = pd.to_datetime(df['closed_date'], errors='coerce')
    df['ward'] = pd.to_numeric(df['ward'], errors='coerce')
    df['community_area'] = pd.to_numeric(df['community_area'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Calculate response time in days
    df['response_days'] = (df['closed_date'] - df['created_date']).dt.total_seconds() / 86400

    # Filter out invalid response times (negative or extremely long)
    df.loc[df['response_days'] < 0, 'response_days'] = None
    df.loc[df['response_days'] > 365, 'response_days'] = None

    # Add temporal fields for analysis
    df['created_hour'] = df['created_date'].dt.hour
    df['created_day_of_week'] = df['created_date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['created_month'] = df['created_date'].dt.month

    return df


def fetch_rodent_complaints(days_back: int = 365 * 3) -> pd.DataFrame:
    """Fetch rodent baiting complaints from Chicago 311 data.

    Args:
        days_back: Number of days of historical data to fetch

    Returns:
        DataFrame with rodent complaints (empty DataFrame on error)
    """
    try:
        return _fetch_rodent_complaints_cached(days_back)
    except Exception as e:
        st.warning(f"Could not connect to Chicago Data Portal: {e}")
        return pd.DataFrame()


ALDERMEN_COLUMNS = ['ward', 'alderman', 'address', 'city', 'state',
                    'zipcode', 'ward_phone', 'website']


def _empty_aldermen() -> pd.DataFrame:
    return pd.DataFrame(columns=ALDERMEN_COLUMNS).astype({'ward': 'float64'})


@st.cache_data(ttl=86400)  # Cache for 24 hours; raises on failure (not cached)
def _fetch_aldermen_cached() -> pd.DataFrame:
    results = _socrata_get(
        DATASET_WARD_OFFICES,
        select=", ".join(ALDERMEN_COLUMNS),
        limit=60  # 50 wards + buffer
    )

    df = pd.DataFrame.from_records(results)

    if df.empty:
        return _empty_aldermen()

    for col in ALDERMEN_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df['ward'] = pd.to_numeric(df['ward'], errors='coerce')
    # Socrata returns URL-typed fields as dicts like {'url': '...'}
    df['website'] = df['website'].apply(
        lambda v: v.get('url') if isinstance(v, dict) else v
    )
    df = df.sort_values('ward')

    return df


def fetch_aldermen() -> pd.DataFrame:
    """Fetch current alderman information by ward.

    Returns:
        DataFrame with alderman name, ward, contact info. Always contains
        ALDERMEN_COLUMNS (empty but well-formed on error) so callers can
        merge without guarding.
    """
    try:
        return _fetch_aldermen_cached()
    except Exception as e:
        st.warning(f"Could not fetch alderman data: {e}")
        return _empty_aldermen()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_dataset_metadata() -> dict:
    """Get metadata about the 311 dataset from Chicago Data Portal.

    Returns:
        Dict with dataset update timestamp and info
    """
    import requests

    try:
        # Query the Socrata metadata API
        url = f"https://{CHICAGO_DATA_PORTAL}/api/views/{DATASET_311_REQUESTS}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # rowsUpdatedAt is Unix timestamp
        rows_updated = data.get('rowsUpdatedAt')
        if rows_updated:
            last_updated = datetime.fromtimestamp(rows_updated)
        else:
            last_updated = None

        return {
            'last_updated': last_updated,
            'dataset_name': data.get('name', '311 Service Requests'),
            'row_count': data.get('cachedContents', {}).get('rows', 'Unknown')
        }
    except Exception:
        return {
            'last_updated': None,
            'dataset_name': '311 Service Requests',
            'row_count': 'Unknown'
        }


def get_data_freshness() -> dict:
    """Get information about data freshness.

    Returns:
        Dict with last_updated, record_count, date_range
    """
    df = fetch_rodent_complaints(days_back=30)  # Quick fetch for freshness check

    if df.empty:
        return {
            'last_updated': None,
            'record_count': 0,
            'date_range': (None, None)
        }

    return {
        'last_updated': datetime.now(),
        'record_count': len(df),
        'newest_complaint': df['created_date'].max(),
        'oldest_complaint': df['created_date'].min()
    }


# Quick test
if __name__ == "__main__":
    print("Fetching rodent complaints...")
    df = fetch_rodent_complaints(days_back=30)
    print(f"Fetched {len(df)} complaints from last 30 days")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Wards with data: {df['ward'].nunique()}")
    print(f"\nSample data:")
    print(df.head())

    print("\n\nFetching aldermen...")
    aldermen = fetch_aldermen()
    print(f"Fetched {len(aldermen)} aldermen")
    print(aldermen.head())
