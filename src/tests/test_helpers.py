"""
Tests for utility functions.
"""

import pytest
import tempfile
import os
from src.utils.helpers import (
    load_json_file,
    save_json_file,
    load_csv_file,
    format_file_size,
    ensure_directory_exists
)


class TestHelpers:
    """Test class for helper functions."""
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0B"
        assert format_file_size(1024) == "1.0KB"
        assert format_file_size(1024 * 1024) == "1.0MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0GB"
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "test_dir")
            assert ensure_directory_exists(new_dir) is True
            assert os.path.exists(new_dir) is True
    
    def test_save_and_load_json(self):
        """Test JSON save and load operations."""
        test_data = {"name": "Test", "value": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # Test save
            assert save_json_file(test_data, temp_file_path) is True
            
            # Test load
            loaded_data = load_json_file(temp_file_path)
            assert loaded_data == test_data
        finally:
            # Cleanup
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent files."""
        assert load_json_file("nonexistent.json") == {}
        assert load_csv_file("nonexistent.csv") == []
