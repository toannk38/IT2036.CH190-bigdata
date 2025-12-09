"""
Property-based tests for SymbolManager.

These tests verify universal properties that should hold across all valid inputs
using the Hypothesis library for property-based testing.
"""

import json
import tempfile
import os
from datetime import datetime
from hypothesis import given, strategies as st, settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import pytest

from src.services.symbol_manager import SymbolManager


# Hypothesis strategies for generating test data
@st.composite
def symbol_data(draw):
    """Generate valid symbol data."""
    symbol = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu',), max_codepoint=127),
        min_size=2,
        max_size=5
    ))
    
    return {
        'symbol': symbol,
        'organ_name': draw(st.text(min_size=5, max_size=100)),
        'icb_name2': draw(st.text(min_size=3, max_size=50)),
        'icb_name3': draw(st.text(min_size=3, max_size=50)),
        'icb_name4': draw(st.text(min_size=3, max_size=50)),
        'com_type_code': draw(st.sampled_from(['CT', 'NH', 'CK'])),
        'icb_code1': draw(st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',)))),
        'icb_code2': draw(st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',)))),
        'icb_code3': draw(st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',)))),
        'icb_code4': draw(st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',)))),
    }


@pytest.fixture(scope='function')
def mongo_client():
    """Create a MongoDB client for testing."""
    # Use a test database
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
    
    # Test connection
    try:
        client.admin.command('ping')
    except PyMongoError:
        pytest.skip("MongoDB not available for testing")
    
    yield client
    
    # Cleanup: drop test database
    client.drop_database('test_vietnam_stock_ai')
    client.close()


@pytest.fixture(scope='function')
def symbol_manager(mongo_client):
    """Create a SymbolManager instance for testing."""
    return SymbolManager(mongo_client, database_name='test_vietnam_stock_ai')


class TestSymbolUpsertIdempotence:
    """
    Test Property 3: Symbol upsert idempotence
    **Validates: Requirements 2.4**
    """
    
    @given(symbol_data=symbol_data())
    @settings(max_examples=100, deadline=None)
    def test_symbol_upsert_idempotence(self, symbol_manager, symbol_data):
        """
        **Feature: vietnam-stock-ai-backend, Property 3: Symbol upsert idempotence**
        
        For any symbol loaded from JSON file, if the symbol already exists in the collection,
        the existing record should be updated with new metadata without creating duplicates.
        
        This test verifies that:
        1. Loading the same symbol multiple times doesn't create duplicates
        2. The symbol count remains 1 after multiple upserts
        3. The metadata is updated correctly
        """
        # Create a temporary JSON file with the symbol
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([symbol_data], f)
            temp_file = f.name
        
        try:
            # First load
            count1 = symbol_manager.load_symbols_from_json(temp_file)
            assert count1 == 1, "First load should insert 1 symbol"
            
            # Verify symbol exists
            symbols_after_first = symbol_manager.get_all_symbols()
            assert len(symbols_after_first) == 1, "Should have exactly 1 symbol after first load"
            
            # Modify the symbol data slightly
            modified_data = symbol_data.copy()
            modified_data['organ_name'] = modified_data['organ_name'] + ' - Updated'
            
            # Create new temp file with modified data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
                json.dump([modified_data], f2)
                temp_file2 = f2.name
            
            try:
                # Second load with modified data
                count2 = symbol_manager.load_symbols_from_json(temp_file2)
                assert count2 == 1, "Second load should update 1 symbol"
                
                # Verify still only 1 symbol (no duplicate)
                symbols_after_second = symbol_manager.get_all_symbols()
                assert len(symbols_after_second) == 1, "Should still have exactly 1 symbol after second load (no duplicates)"
                
                # Verify the symbol was updated
                updated_symbol = symbol_manager.get_symbol(symbol_data['symbol'])
                assert updated_symbol is not None, "Symbol should exist"
                assert updated_symbol['organ_name'] == modified_data['organ_name'], "Symbol should be updated with new metadata"
                
                # Third load with same data (idempotence check)
                count3 = symbol_manager.load_symbols_from_json(temp_file2)
                assert count3 == 1, "Third load should update 1 symbol"
                
                # Verify still only 1 symbol
                symbols_after_third = symbol_manager.get_all_symbols()
                assert len(symbols_after_third) == 1, "Should still have exactly 1 symbol after third load"
                
            finally:
                os.unlink(temp_file2)
        
        finally:
            os.unlink(temp_file)
            # Clean up the test data
            symbol_manager.collection.delete_many({})
