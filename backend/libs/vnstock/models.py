from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StockPrice:
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class StockNews:
    symbol: str
    title: str
    publish_date: datetime
    source: str
    url: Optional[str] = None

@dataclass
class StockListing:
    symbol: str
    organ_name: str
    icb_name3: Optional[str] = None
    icb_name2: Optional[str] = None
    icb_name4: Optional[str] = None
