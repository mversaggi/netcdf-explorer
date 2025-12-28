"""
Configuration Parser Module

This module provides utilities for loading and accessing configuration settings
from TOML files. It includes functions for loading configuration files and
safely accessing nested configuration values using dot notation.

Example usage:
    ```python
    # Load configuration from default path (./.netex_config.toml)
    config = load_config()
    
    # Or specify a custom path
    config = load_config("/path/to/config.toml")
    
    # Access configuration values
    debug_mode = get_config_value(config, "flask.debug", False)
    db_host = get_config_value(config, "database.host", "localhost")
    ```

TODO: Update this example to be more realistic
Example configuration file:
    ```toml
    [flask]
    debug = true
    host = "0.0.0.0"
    port = 5000

    [database]
    host = "localhost"
    port = 5432
    name = "myapp_db"
    ```
"""

from pathlib import Path
from typing import Dict, Any
import toml
import logging

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load and parse a TOML configuration file into a dictionary of key-value pairs.
    
    Args:
        config_path: Path to the configuration file.

    Returns:
        A dictionary containing the key-value configuration pairs.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        toml.TomlDecodeError: If the TOML file is malformed.
    """

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    try:
        config = toml.load(config_path)
        logging.info(f"Successfully loaded configuration from {config_path}")
        return config
    except toml.TomlDecodeError as e:
        logging.error(f"Error parsing TOML configuration at {config_path}: {e}")
        raise

def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from the configuration dictionary.
    
    Args:
        config: Configuration dictionary.
        key: Dot-notation key to access nested values (e.g., 'database.host').
        default: Default value to return if the key is not found.
        
    Returns:
        The configuration value or the default if not found.
    """
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value

if __name__ == "__main__":
    # Simple test when run directly
    test_config = {
        "flask": {"debug": True, "host": "0.0.0.0"},
        "database": {"name": "test_db"}
    }
    print(f"Test get_config_value: {get_config_value(test_config, 'flask.debug')}")