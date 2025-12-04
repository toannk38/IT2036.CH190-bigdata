"""Stock prices fixture - loads VCI_1m.csv."""
from backend.tests.infrastructure.utils.data_loader import load_csv_file, parse_timestamp


def load_prices(limit=None):
    """Load price data from VCI_1m.csv.
    
    Returns DataFrame with schema:
    {
        "time": "2024-05-23 10:16:00",
        "open": 37.77,
        "high": 37.77,
        "low": 37.77,
        "close": 37.77,
        "volume": 1500
    }
    """
    df = load_csv_file("VCI_1m.csv")
    
    # Parse timestamp
    df['time'] = pd.to_datetime(df['time'])
    
    # Add symbol
    df['symbol'] = 'VCI'
    
    if limit:
        return df.head(limit)
    
    return df


def get_prices_as_dict(limit=None):
    """Get prices as list of dictionaries."""
    df = load_prices(limit)
    return df.to_dict('records')


import pandas as pd
