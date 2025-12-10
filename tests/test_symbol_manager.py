"""
Unit tests for SymbolManager.

These tests verify specific functionality of the SymbolManager class.
"""

import json
import tempfile
import os
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.services.symbol_manager import SymbolManager


@pytest.fixture(scope='function')
def mongo_client():
    """Create a MongoDB client for testing."""
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
    
    # Test connection
    try:
        client.admin.command('ping')
    except PyMongoError:
        pytest.skip("MongoDB not available for testing")
    
    yield client
    
    # Cleanup: drop test database (only if connection is still open)
    try:
        client.drop_database('test_vietnam_stock_ai_unit')
        client.close()
    except PyMongoError:
        # Connection already closed, skip cleanup
        pass


@pytest.fixture(scope='function')
def symbol_manager(mongo_client):
    """Create a SymbolManager instance for testing."""
    return SymbolManager(mongo_client, database_name='test_vietnam_stock_ai_unit')


class TestSymbolManagerJSONParsing:
    """Test JSON parsing and loading functionality."""
    
    def test_load_symbols_from_valid_json(self, symbol_manager):
        """Test loading symbols from a valid JSON file."""
        # Use the actual VN30 data file
        vn30_file = 'data/vn30.json'
        
        count = symbol_manager.load_symbols_from_json(vn30_file)
        
        assert count == 30, "Should load 30 symbols from VN30 file"
        
        # Verify symbols are in database
        all_symbols = symbol_manager.get_all_symbols()
        assert len(all_symbols) == 30
        
        # Verify required fields are present
        for symbol in all_symbols:
            assert 'symbol' in symbol
            assert 'organ_name' in symbol
            assert 'active' in symbol
            assert 'created_at' in symbol
            assert 'updated_at' in symbol
    
    def test_load_symbols_from_nonexistent_file(self, symbol_manager):
        """Test error handling when JSON file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            symbol_manager.load_symbols_from_json('nonexistent_file.json')
    
    def test_load_symbols_from_invalid_json(self, symbol_manager):
        """Test error handling for invalid JSON format."""
        # Create a temp file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                symbol_manager.load_symbols_from_json(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_symbols_with_missing_symbol_field(self, symbol_manager):
        """Test handling of symbol data without 'symbol' field."""
        # Create JSON with one valid and one invalid symbol
        data = [
            {
                'symbol': 'TEST',
                'organ_name': 'Test Company',
                'icb_name2': 'Test Industry'
            },
            {
                # Missing 'symbol' field
                'organ_name': 'Invalid Company',
                'icb_name2': 'Test Industry'
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            # Should load only the valid symbol
            count = symbol_manager.load_symbols_from_json(temp_file)
            assert count == 1, "Should load only the valid symbol"
            
            # Verify only one symbol in database
            all_symbols = symbol_manager.get_all_symbols()
            assert len(all_symbols) == 1
            assert all_symbols[0]['symbol'] == 'TEST'
        finally:
            os.unlink(temp_file)
    
    def test_load_symbols_sets_active_flag_by_default(self, symbol_manager):
        """Test that symbols without 'active' field are set to active=True by default."""
        data = [
            {
                'symbol': 'TEST1',
                'organ_name': 'Test Company 1'
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            symbol_manager.load_symbols_from_json(temp_file)
            
            # Verify active flag is set to True
            symbol = symbol_manager.get_symbol('TEST1')
            assert symbol is not None
            assert symbol['active'] is True
        finally:
            os.unlink(temp_file)


class TestSymbolRetrieval:
    """Test symbol retrieval with different filters."""
    
    def test_get_active_symbols_returns_list_of_strings(self, symbol_manager):
        """Test that get_active_symbols returns a list of symbol codes."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        active_symbols = symbol_manager.get_active_symbols()
        
        assert isinstance(active_symbols, list)
        assert len(active_symbols) > 0
        assert all(isinstance(s, str) for s in active_symbols)
    
    def test_get_symbol_by_code(self, symbol_manager):
        """Test retrieving a specific symbol by code."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        # Get a specific symbol
        symbol = symbol_manager.get_symbol('VNM')
        
        assert symbol is not None
        assert symbol['symbol'] == 'VNM'
        assert 'organ_name' in symbol
    
    def test_get_nonexistent_symbol(self, symbol_manager):
        """Test retrieving a symbol that doesn't exist."""
        symbol = symbol_manager.get_symbol('NONEXISTENT')
        assert symbol is None
    
    def test_get_all_symbols_active_only(self, symbol_manager):
        """Test getting all symbols with active_only filter."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        # Deactivate one symbol
        symbol_manager.update_symbol('VNM', {'active': False})
        
        # Get all active symbols
        active_symbols = symbol_manager.get_all_symbols(active_only=True)
        
        assert len(active_symbols) == 29  # 30 - 1 deactivated
        assert all(s['active'] is True for s in active_symbols)
        assert not any(s['symbol'] == 'VNM' for s in active_symbols)
    
    def test_get_all_symbols_including_inactive(self, symbol_manager):
        """Test getting all symbols including inactive ones."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        # Deactivate one symbol
        symbol_manager.update_symbol('VNM', {'active': False})
        
        # Get all symbols (including inactive)
        all_symbols = symbol_manager.get_all_symbols(active_only=False)
        
        assert len(all_symbols) == 30
        assert any(s['symbol'] == 'VNM' and s['active'] is False for s in all_symbols)


class TestSymbolUpdate:
    """Test symbol metadata update functionality."""
    
    def test_update_existing_symbol(self, symbol_manager):
        """Test updating metadata of an existing symbol."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        # Update a symbol
        result = symbol_manager.update_symbol('VNM', {
            'organ_name': 'Updated Company Name',
            'custom_field': 'custom_value'
        })
        
        assert result is True
        
        # Verify update
        symbol = symbol_manager.get_symbol('VNM')
        assert symbol['organ_name'] == 'Updated Company Name'
        assert symbol['custom_field'] == 'custom_value'
        assert 'updated_at' in symbol
    
    def test_update_nonexistent_symbol(self, symbol_manager):
        """Test updating a symbol that doesn't exist."""
        result = symbol_manager.update_symbol('NONEXISTENT', {
            'organ_name': 'Test'
        })
        
        assert result is False
    
    def test_update_symbol_with_empty_metadata(self, symbol_manager):
        """Test updating a symbol with empty metadata."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        result = symbol_manager.update_symbol('VNM', {})
        
        assert result is False
    
    def test_update_symbol_adds_updated_at_timestamp(self, symbol_manager):
        """Test that update_symbol adds updated_at timestamp."""
        # Load VN30 data
        symbol_manager.load_symbols_from_json('data/vn30.json')
        
        # Get original timestamp
        original_symbol = symbol_manager.get_symbol('VNM')
        original_updated_at = original_symbol['updated_at']
        
        # Update symbol
        symbol_manager.update_symbol('VNM', {'test_field': 'test_value'})
        
        # Verify updated_at changed
        updated_symbol = symbol_manager.get_symbol('VNM')
        assert updated_symbol['updated_at'] >= original_updated_at


class TestSymbolManagerInitialization:
    """Test SymbolManager initialization and setup."""
    
    def test_initialization_creates_indexes(self, mongo_client):
        """Test that initialization creates necessary indexes."""
        manager = SymbolManager(mongo_client, database_name='test_vietnam_stock_ai_init')
        
        # Get index information
        indexes = list(manager.collection.list_indexes())
        index_names = [idx['name'] for idx in indexes]
        
        # Should have at least _id_, symbol, and active indexes
        assert '_id_' in index_names
        assert 'symbol_1' in index_names
        assert 'active_1' in index_names
        
        # Cleanup
        mongo_client.drop_database('test_vietnam_stock_ai_init')
    
    def test_initialization_with_custom_database(self, mongo_client):
        """Test initialization with custom database name."""
        custom_db_name = 'custom_test_db'
        manager = SymbolManager(mongo_client, database_name=custom_db_name)
        
        assert manager.db.name == custom_db_name
        
        # Cleanup
        mongo_client.drop_database(custom_db_name)


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_load_symbols_with_non_list_json(self, symbol_manager):
        """Test error handling when JSON is not a list."""
        data = {'symbol': 'TEST'}  # Dict instead of list
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain a list"):
                symbol_manager.load_symbols_from_json(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_operations_with_closed_connection(self, mongo_client):
        """Test that operations handle connection errors gracefully."""
        from pymongo.errors import InvalidOperation
        
        manager = SymbolManager(mongo_client, database_name='test_vietnam_stock_ai_error')
        
        # Close the connection
        mongo_client.close()
        
        # Operations should raise InvalidOperation (a subclass of PyMongoError)
        with pytest.raises(InvalidOperation):
            manager.get_active_symbols()
