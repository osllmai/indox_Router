"""
Unit tests for the config module.
"""

import os
import json
import tempfile
from unittest.mock import patch, mock_open

import pytest

from indoxRouter.config import Config, get_config


class TestConfig:
    """Tests for the Config class."""

    def test_init_with_default_path(self):
        """Test initialization with default path."""
        with patch('os.path.expanduser', return_value='/mock/path'):
            with patch('os.path.exists', return_value=False):
                config = Config()
                assert config.config_path == '/mock/path'
                assert config.config == {}

    def test_init_with_custom_path(self):
        """Test initialization with custom path."""
        with patch('os.path.exists', return_value=False):
            config = Config('/custom/path')
            assert config.config_path == '/custom/path'
            assert config.config == {}

    def test_load_config_from_file(self):
        """Test loading config from file."""
        mock_config = {'provider_keys': {'openai': 'test-key'}}
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            json.dump(mock_config, temp_file)
            temp_file_path = temp_file.name
        
        try:
            config = Config(temp_file_path)
            assert config.config == mock_config
        finally:
            os.unlink(temp_file_path)

    def test_load_from_env(self):
        """Test loading config from environment variables."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
            with patch('os.path.exists', return_value=False):
                config = Config()
                assert config.config['provider_keys']['openai'] == 'env-key'

    def test_get_provider_key(self):
        """Test getting provider key."""
        config = Config()
        config.config = {'provider_keys': {'openai': 'test-key'}}
        
        # Test getting existing key
        assert config.get_provider_key('openai') == 'test-key'
        
        # Test getting non-existent key
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'env-key'}):
            assert config.get_provider_key('anthropic') == 'env-key'
        
        # Test getting non-existent key with no env var
        assert config.get_provider_key('nonexistent') is None

    def test_set_provider_key(self):
        """Test setting provider key."""
        config = Config()
        
        # Test setting key in empty config
        config.set_provider_key('openai', 'test-key')
        assert config.config['provider_keys']['openai'] == 'test-key'
        
        # Test overwriting existing key
        config.set_provider_key('openai', 'new-key')
        assert config.config['provider_keys']['openai'] == 'new-key'

    def test_save_config(self):
        """Test saving config to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'config.json')
            config = Config(config_path)
            config.config = {'provider_keys': {'openai': 'test-key'}}
            
            config.save_config()
            
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
                assert saved_config == config.config

    def test_get(self):
        """Test getting config value."""
        config = Config()
        config.config = {'test_key': 'test_value'}
        
        # Test getting existing key
        assert config.get('test_key') == 'test_value'
        
        # Test getting non-existent key
        assert config.get('nonexistent') is None
        
        # Test getting non-existent key with default
        assert config.get('nonexistent', 'default') == 'default'

    def test_set(self):
        """Test setting config value."""
        config = Config()
        
        # Test setting new key
        config.set('test_key', 'test_value')
        assert config.config['test_key'] == 'test_value'
        
        # Test overwriting existing key
        config.set('test_key', 'new_value')
        assert config.config['test_key'] == 'new_value'


class TestGetConfig:
    """Tests for the get_config function."""

    def test_get_config_singleton(self):
        """Test that get_config returns a singleton instance."""
        with patch('indoxRouter.config.Config') as mock_config:
            mock_config.return_value = 'test-instance'
            
            # First call should create a new instance
            instance1 = get_config()
            assert instance1 == 'test-instance'
            mock_config.assert_called_once()
            
            # Second call should return the same instance
            mock_config.reset_mock()
            instance2 = get_config()
            assert instance2 == 'test-instance'
            mock_config.assert_not_called()

    def test_get_config_with_path(self):
        """Test get_config with custom path."""
        with patch('indoxRouter.config.Config') as mock_config:
            mock_config.return_value = 'test-instance'
            
            # Call with custom path
            instance = get_config('/custom/path')
            assert instance == 'test-instance'
            mock_config.assert_called_once_with('/custom/path') 