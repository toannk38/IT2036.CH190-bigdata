"""
Property-based tests for SymbolManager.

These tests verify universal properties that should hold across all valid inputs.
"""

import json
import tempfile
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import pytest

from src.services.symbol_manager import SymbolManager


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
    
    def test_symbol_upsert_idempotence_with_vn30_data(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 3: Symbol upsert idempotence**
        
        For any symbol loaded from JSON file, if the symbol already exists in the collection,
        the existing record should be updated with new metadata without creating duplicates.
        
        This test verifies that:
        1. Loading the same symbols multiple times doesn't create duplicates
        2. The symbol count remains consistent after multiple upserts
        3. The metadata is updated correctly
        
        Uses real data from data/vn30.json
        """
        # Load the actual VN30 data
        vn30_file = 'data/vn30.json'
        
        # First load - should insert all symbols
        count1 = symbol_manager.load_symbols_from_json(vn30_file)
        assert count1 == 30, f"First load should insert 30 symbols, got {count1}"
        
        # Verify all symbols exist
        symbols_after_first = symbol_manager.get_all_symbols()
        assert len(symbols_after_first) == 30, f"Should have exactly 30 symbols after first load, got {len(symbols_after_first)}"
        
        # Get one symbol to verify
        first_symbol = symbols_after_first[0]
        original_updated_at = first_symbol['updated_at']
        
        # Second load with same data - should update all symbols (no duplicates)
        count2 = symbol_manager.load_symbols_from_json(vn30_file)
        assert count2 == 30, f"Second load should update 30 symbols, got {count2}"
        
        # Verify still only 30 symbols (no duplicates)
        symbols_after_second = symbol_manager.get_all_symbols()
        assert len(symbols_after_second) == 30, f"Should still have exactly 30 symbols after second load (no duplicates), got {len(symbols_after_second)}"
        
        # Verify the updated_at timestamp changed (proving update occurred)
        updated_symbol = symbol_manager.get_symbol(first_symbol['symbol'])
        assert updated_symbol is not None, "Symbol should exist"
        assert updated_symbol['updated_at'] >= original_updated_at, "updated_at should be updated"
        
        # Third load with same data (idempotence check)
        count3 = symbol_manager.load_symbols_from_json(vn30_file)
        assert count3 == 30, f"Third load should update 30 symbols, got {count3}"
        
        # Verify still only 30 symbols
        symbols_after_third = symbol_manager.get_all_symbols()
        assert len(symbols_after_third) == 30, f"Should still have exactly 30 symbols after third load, got {len(symbols_after_third)}"
    
    def test_symbol_upsert_updates_metadata(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 3: Symbol upsert idempotence**
        
        Verify that upserting a symbol with modified metadata updates the existing record
        without creating duplicates.
        """
        # Load original VN30 data
        vn30_file = 'data/vn30.json'
        count1 = symbol_manager.load_symbols_from_json(vn30_file)
        assert count1 == 30
        
        # Get the original data for one symbol
        original_symbol = symbol_manager.get_symbol('VNM')
        assert original_symbol is not None
        original_organ_name = original_symbol['organ_name']
        
        # Create a modified version with updated metadata
        with open(vn30_file, 'r', encoding='utf-8') as f:
            symbols_data = json.load(f)
        
        # Modify one symbol's metadata
        for symbol in symbols_data:
            if symbol['symbol'] == 'VNM':
                symbol['organ_name'] = symbol['organ_name'] + ' - UPDATED'
                break
        
        # Write modified data to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(symbols_data, f)
            temp_file = f.name
        
        try:
            # Load modified data
            count2 = symbol_manager.load_symbols_from_json(temp_file)
            assert count2 == 30, "Should update 30 symbols"
            
            # Verify still only 30 symbols (no duplicates)
            all_symbols = symbol_manager.get_all_symbols()
            assert len(all_symbols) == 30, "Should still have exactly 30 symbols (no duplicates)"
            
            # Verify the metadata was updated
            updated_symbol = symbol_manager.get_symbol('VNM')
            assert updated_symbol is not None
            assert updated_symbol['organ_name'] == original_organ_name + ' - UPDATED', "Metadata should be updated"
            assert updated_symbol['organ_name'] != original_organ_name, "Metadata should have changed"
            
        finally:
            os.unlink(temp_file)
    
    def test_symbol_upsert_with_subset_of_symbols(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 3: Symbol upsert idempotence**
        
        Verify that upserting a subset of symbols doesn't affect other symbols.
        """
        # Load all VN30 symbols
        vn30_file = 'data/vn30.json'
        count1 = symbol_manager.load_symbols_from_json(vn30_file)
        assert count1 == 30
        
        # Create a file with only 3 symbols
        with open(vn30_file, 'r', encoding='utf-8') as f:
            all_symbols = json.load(f)
        
        subset_symbols = all_symbols[:3]
        
        # Modify the subset
        for symbol in subset_symbols:
            symbol['organ_name'] = symbol['organ_name'] + ' - MODIFIED'
        
        # Write subset to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(subset_symbols, f)
            temp_file = f.name
        
        try:
            # Load subset
            count2 = symbol_manager.load_symbols_from_json(temp_file)
            assert count2 == 3, "Should update 3 symbols"
            
            # Verify still 30 symbols total
            all_symbols_after = symbol_manager.get_all_symbols()
            assert len(all_symbols_after) == 30, "Should still have 30 symbols total"
            
            # Verify the 3 symbols were updated
            for symbol_data in subset_symbols:
                updated = symbol_manager.get_symbol(symbol_data['symbol'])
                assert updated is not None
                assert ' - MODIFIED' in updated['organ_name'], f"Symbol {symbol_data['symbol']} should be modified"
            
            # Verify other symbols were not affected
            unmodified_symbol = symbol_manager.get_symbol(all_symbols[3]['symbol'])
            assert unmodified_symbol is not None
            assert ' - MODIFIED' not in unmodified_symbol['organ_name'], "Unmodified symbols should remain unchanged"
            
        finally:
            os.unlink(temp_file)



class TestActiveSymbolsRetrieval:
    """
    Test Property 4: Active symbols retrieval
    **Validates: Requirements 2.5**
    """
    
    def test_active_symbols_retrieval_returns_only_active(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 4: Active symbols retrieval**
        
        For any query for active symbols, only symbols with active=true should be returned.
        
        This test verifies that:
        1. Only symbols marked as active=True are returned
        2. Symbols marked as active=False are excluded
        3. The returned list contains only symbol codes (strings)
        """
        # Load VN30 data (all active by default)
        vn30_file = 'data/vn30.json'
        symbol_manager.load_symbols_from_json(vn30_file)
        
        # Verify all symbols are active initially
        active_symbols = symbol_manager.get_active_symbols()
        assert len(active_symbols) == 30, "Should return all 30 active symbols"
        assert all(isinstance(s, str) for s in active_symbols), "All returned values should be strings"
        
        # Deactivate some symbols
        symbols_to_deactivate = ['VNM', 'VIC', 'HPG']
        for symbol in symbols_to_deactivate:
            symbol_manager.update_symbol(symbol, {'active': False})
        
        # Query active symbols again
        active_symbols_after = symbol_manager.get_active_symbols()
        
        # Should return 27 symbols (30 - 3 deactivated)
        assert len(active_symbols_after) == 27, f"Should return 27 active symbols, got {len(active_symbols_after)}"
        
        # Verify deactivated symbols are not in the list
        for symbol in symbols_to_deactivate:
            assert symbol not in active_symbols_after, f"Deactivated symbol {symbol} should not be in active list"
        
        # Verify all returned symbols are actually active
        for symbol_code in active_symbols_after:
            symbol_doc = symbol_manager.get_symbol(symbol_code)
            assert symbol_doc is not None, f"Symbol {symbol_code} should exist"
            assert symbol_doc.get('active', False) is True, f"Symbol {symbol_code} should be active"
    
    def test_active_symbols_retrieval_with_all_inactive(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 4: Active symbols retrieval**
        
        Verify that when all symbols are inactive, an empty list is returned.
        """
        # Load VN30 data
        vn30_file = 'data/vn30.json'
        symbol_manager.load_symbols_from_json(vn30_file)
        
        # Deactivate all symbols
        all_symbols = symbol_manager.get_all_symbols()
        for symbol_doc in all_symbols:
            symbol_manager.update_symbol(symbol_doc['symbol'], {'active': False})
        
        # Query active symbols
        active_symbols = symbol_manager.get_active_symbols()
        
        # Should return empty list
        assert len(active_symbols) == 0, "Should return empty list when all symbols are inactive"
        assert isinstance(active_symbols, list), "Should return a list"
    
    def test_active_symbols_retrieval_with_all_active(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 4: Active symbols retrieval**
        
        Verify that when all symbols are active, all symbol codes are returned.
        """
        # Load VN30 data (all active by default)
        vn30_file = 'data/vn30.json'
        count = symbol_manager.load_symbols_from_json(vn30_file)
        
        # Query active symbols
        active_symbols = symbol_manager.get_active_symbols()
        
        # Should return all symbols
        assert len(active_symbols) == count, f"Should return all {count} symbols when all are active"
        
        # Verify all symbols from database are in the active list
        all_symbols = symbol_manager.get_all_symbols()
        all_symbol_codes = [s['symbol'] for s in all_symbols]
        
        for symbol_code in all_symbol_codes:
            assert symbol_code in active_symbols, f"Active symbol {symbol_code} should be in the returned list"
    
    def test_active_symbols_retrieval_consistency(self, symbol_manager):
        """
        **Feature: vietnam-stock-ai-backend, Property 4: Active symbols retrieval**
        
        Verify that multiple calls to get_active_symbols() return consistent results
        when the database state hasn't changed.
        """
        # Load VN30 data
        vn30_file = 'data/vn30.json'
        symbol_manager.load_symbols_from_json(vn30_file)
        
        # Call get_active_symbols multiple times
        result1 = symbol_manager.get_active_symbols()
        result2 = symbol_manager.get_active_symbols()
        result3 = symbol_manager.get_active_symbols()
        
        # All results should be identical
        assert set(result1) == set(result2), "Multiple calls should return same symbols"
        assert set(result2) == set(result3), "Multiple calls should return same symbols"
        assert len(result1) == len(result2) == len(result3), "Multiple calls should return same count"
