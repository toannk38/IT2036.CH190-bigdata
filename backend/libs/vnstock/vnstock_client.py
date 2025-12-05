import time
import pandas as pd
from typing import List, Optional
from datetime import datetime
import vnstock as vnstock_lib

from .models import StockPrice, StockNews, StockListing
from .exceptions import VnstockError, RateLimitError, DataNotFoundError
from .cache import cached

class VnstockClient:
    def __init__(self, source: str = 'VCI', rate_limit: float = 0.5):
        self.source = source
        self.rate_limit = rate_limit
        self._last_call = 0
    
    def _rate_limit_check(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_call = time.time()
    
    def _handle_error(self, e: Exception, context: str):
        if isinstance(e, (RateLimitError, DataNotFoundError, VnstockError)):
            raise
        if "rate limit" in str(e).lower():
            raise RateLimitError(f"Rate limit exceeded: {context}")
        elif "not found" in str(e).lower():
            raise DataNotFoundError(f"Data not found: {context}")
        raise VnstockError(f"Error in {context}: {str(e)}")
    
    @cached(ttl=3600)
    def get_all_symbols(self) -> List[StockListing]:
        self._rate_limit_check()
        try:
            listing = vnstock_lib.Listing(source=self.source)
            df1 = listing.all_symbols()
            df2 = listing.symbols_by_industries()
            
            df = df1.merge(df2, on='symbol', how='inner', suffixes=('_1', '_2'))
            if 'organ_name_1' in df.columns and 'organ_name_2' in df.columns:
                df['organ_name'] = df['organ_name_2'].combine_first(df['organ_name_1'])
                df = df.drop(columns=['organ_name_1', 'organ_name_2'])
            
            return [
                StockListing(
                    symbol=row['symbol'],
                    organ_name=row['organ_name'],
                    icb_name3=row.get('icb_name3'),
                    icb_name2=row.get('icb_name2'),
                    icb_name4=row.get('icb_name4')
                )
                for _, row in df.iterrows()
            ]
        except Exception as e:
            self._handle_error(e, "get_all_symbols")
    
    def get_price_history(
        self, 
        symbol: str, 
        start: str, 
        end: str, 
        interval: str = '1D'
    ) -> List[StockPrice]:
        self._rate_limit_check()
        try:
            quote = vnstock_lib.Quote(symbol=symbol, source=self.source)
            df = quote.history(start=start, end=end, interval=interval)
            
            if df.empty:
                raise DataNotFoundError(f"No price data for {symbol}")
            
            return [
                StockPrice(
                    symbol=symbol,
                    time=pd.to_datetime(row['time']),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume'])
                )
                for _, row in df.iterrows()
            ]
        except Exception as e:
            self._handle_error(e, f"get_price_history for {symbol}")
    
    def get_news(self, symbol: str) -> List[StockNews]:
        self._rate_limit_check()
        try:
            company = vnstock_lib.Company(symbol=symbol, source=self.source)
            df = company.news()
            
            if df.empty:
                return []
            
            return [
                StockNews(
                    symbol=symbol,
                    title=row['title'],
                    publish_date=pd.to_datetime(row['publishDate']),
                    source=row.get('source', 'Unknown'),
                    url=row.get('url')
                )
                for _, row in df.iterrows()
            ]
        except Exception as e:
            self._handle_error(e, f"get_news for {symbol}")
