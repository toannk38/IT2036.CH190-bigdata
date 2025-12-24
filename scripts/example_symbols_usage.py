#!/usr/bin/env python3
"""
Example usage of the /symbols API endpoint.
Demonstrates how to retrieve and work with active symbols data.
"""

import requests
import json
from typing import List, Dict, Any

class SymbolsAPIClient:
    """Client for interacting with the Vietnam Stock AI Symbols API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API service
        """
        self.base_url = base_url.rstrip('/')
    
    def get_active_symbols(self) -> Dict[str, Any]:
        """
        Get all active symbols from the API.
        
        Returns:
            Dictionary containing symbols data
            
        Raises:
            requests.RequestException: If API request fails
        """
        response = requests.get(f"{self.base_url}/symbols")
        response.raise_for_status()
        return response.json()
    
    def get_symbols_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """
        Filter symbols by industry (ICB name).
        
        Args:
            industry: Industry name to filter by
            
        Returns:
            List of symbols in the specified industry
        """
        data = self.get_active_symbols()
        symbols = data['symbols']
        
        return [
            symbol for symbol in symbols
            if (symbol.get('icb_name2', '').lower() == industry.lower() or
                symbol.get('icb_name3', '').lower() == industry.lower() or
                symbol.get('icb_name4', '').lower() == industry.lower())
        ]
    
    def get_symbols_by_type(self, company_type: str) -> List[Dict[str, Any]]:
        """
        Filter symbols by company type.
        
        Args:
            company_type: Company type code (NH=Bank, CT=Company, CK=Securities)
            
        Returns:
            List of symbols of the specified type
        """
        data = self.get_active_symbols()
        symbols = data['symbols']
        
        return [
            symbol for symbol in symbols
            if symbol.get('com_type_code', '').upper() == company_type.upper()
        ]
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """
        Search symbols by name or symbol code.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching symbols
        """
        data = self.get_active_symbols()
        symbols = data['symbols']
        query_lower = query.lower()
        
        return [
            symbol for symbol in symbols
            if (query_lower in symbol['symbol'].lower() or
                query_lower in symbol.get('organ_name', '').lower())
        ]


def example_basic_usage():
    """Example: Basic usage of the symbols API."""
    print("📊 Basic Usage Example")
    print("-" * 30)
    
    client = SymbolsAPIClient()
    
    try:
        # Get all active symbols
        data = client.get_active_symbols()
        
        print(f"Total symbols in database: {data['total']}")
        print(f"Active symbols: {data['active_count']}")
        print(f"Retrieved {len(data['symbols'])} symbols")
        
        # Show first 5 symbols
        print("\nFirst 5 active symbols:")
        for i, symbol in enumerate(data['symbols'][:5], 1):
            print(f"  {i}. {symbol['symbol']} - {symbol['organ_name']}")
            if symbol.get('icb_name3'):
                print(f"     Industry: {symbol['icb_name3']}")
        
    except requests.RequestException as e:
        print(f"❌ Error: {e}")


def example_filter_by_industry():
    """Example: Filter symbols by industry."""
    print("\n🏭 Filter by Industry Example")
    print("-" * 35)
    
    client = SymbolsAPIClient()
    
    try:
        # Get banking symbols
        banks = client.get_symbols_by_industry("Ngân hàng")
        print(f"Found {len(banks)} banking symbols:")
        
        for bank in banks[:10]:  # Show first 10
            print(f"  • {bank['symbol']} - {bank['organ_name']}")
        
        # Get real estate symbols
        real_estate = client.get_symbols_by_industry("Bất động sản")
        print(f"\nFound {len(real_estate)} real estate symbols:")
        
        for re_symbol in real_estate[:5]:  # Show first 5
            print(f"  • {re_symbol['symbol']} - {re_symbol['organ_name']}")
            
    except requests.RequestException as e:
        print(f"❌ Error: {e}")


def example_filter_by_company_type():
    """Example: Filter symbols by company type."""
    print("\n🏢 Filter by Company Type Example")
    print("-" * 40)
    
    client = SymbolsAPIClient()
    
    try:
        # Get banks (NH = Ngân hàng)
        banks = client.get_symbols_by_type("NH")
        print(f"Banks (NH): {len(banks)} symbols")
        
        # Get companies (CT = Công ty)
        companies = client.get_symbols_by_type("CT")
        print(f"Companies (CT): {len(companies)} symbols")
        
        # Get securities companies (CK = Chứng khoán)
        securities = client.get_symbols_by_type("CK")
        print(f"Securities (CK): {len(securities)} symbols")
        
        # Show some examples
        if banks:
            print(f"\nExample banks:")
            for bank in banks[:3]:
                print(f"  • {bank['symbol']} - {bank['organ_name']}")
                
    except requests.RequestException as e:
        print(f"❌ Error: {e}")


def example_search_symbols():
    """Example: Search symbols by name or code."""
    print("\n🔍 Search Symbols Example")
    print("-" * 30)
    
    client = SymbolsAPIClient()
    
    try:
        # Search for Vingroup related companies
        vingroup_results = client.search_symbols("vin")
        print(f"Search 'vin': {len(vingroup_results)} results")
        
        for result in vingroup_results:
            print(f"  • {result['symbol']} - {result['organ_name']}")
        
        # Search for FPT
        fpt_results = client.search_symbols("FPT")
        print(f"\nSearch 'FPT': {len(fpt_results)} results")
        
        for result in fpt_results:
            print(f"  • {result['symbol']} - {result['organ_name']}")
            
    except requests.RequestException as e:
        print(f"❌ Error: {e}")


def example_industry_analysis():
    """Example: Analyze industry distribution."""
    print("\n📈 Industry Analysis Example")
    print("-" * 35)
    
    client = SymbolsAPIClient()
    
    try:
        data = client.get_active_symbols()
        symbols = data['symbols']
        
        # Count by industry
        industry_count = {}
        for symbol in symbols:
            industry = symbol.get('icb_name3', 'Unknown')
            industry_count[industry] = industry_count.get(industry, 0) + 1
        
        # Sort by count
        sorted_industries = sorted(industry_count.items(), key=lambda x: x[1], reverse=True)
        
        print("Industry distribution (top 10):")
        for industry, count in sorted_industries[:10]:
            print(f"  {industry}: {count} symbols")
            
    except requests.RequestException as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples."""
    print("🚀 Vietnam Stock AI - Symbols API Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_filter_by_industry()
    example_filter_by_company_type()
    example_search_symbols()
    example_industry_analysis()
    
    print("\n✅ All examples completed!")
    print("\n💡 Tips:")
    print("  - Use the SymbolsAPIClient class in your own applications")
    print("  - Filter symbols by industry, company type, or search terms")
    print("  - Combine with other API endpoints for comprehensive analysis")


if __name__ == "__main__":
    main()