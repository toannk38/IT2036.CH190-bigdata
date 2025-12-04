"""Stock news fixture - loads VCB_news.csv."""
from backend.tests.infrastructure.utils.data_loader import load_csv_file
import pandas as pd


def load_news(limit=None):
    """Load news data from VCB_news.csv.
    
    Returns DataFrame with schema:
    {
        "id": 8910472,
        "news_title": "VCB: Thông báo...",
        "news_sub_title": "",
        "news_image_url": "https://...",
        "news_source_link": "https://...",
        "created_at": 1764612216000,
        "news_short_content": "Ngân hàng...",
        "news_full_content": "<p>...</p>",
        "close_price": 57500,
        "ref_price": 57400,
        "floor": 53400,
        "ceiling": 61400,
        "price_change_pct": 0.00174216
    }
    """
    df = load_csv_file("VCB_news.csv")
    
    # Add symbol
    df['symbol'] = 'VCB'
    
    # Convert timestamp
    df['created_at'] = pd.to_datetime(df['created_at'], unit='ms')
    
    if limit:
        return df.head(limit)
    
    return df


def get_news_as_dict(limit=None):
    """Get news as list of dictionaries."""
    df = load_news(limit)
    return df.to_dict('records')
