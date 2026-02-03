"""
Configuration Parser Module

This module provides utilities for loading configuration settings from TOML files
with environment variable overrides. Configuration is loaded hierarchically:
1. Values from the TOML config file
2. Environment variables override TOML values (if set)

See README.md for a list of supported environment variables.

Example usage:
    ```python
    from pathlib import Path
    from netex.conf.config_parser import load_configs
    from netex.conf.config_parser_constants import (
        FLASK_TABLE, FLASK_DEBUG,
        OBJ_STORE_TABLE, OBJ_STORE_ENDPOINT,
        LOGGER_TABLE, LOGGER_LEVEL,
    )

    # Load configuration from a TOML file
    config = load_configs(Path("conf/netex.toml"))

    # Access configuration values
    debug_mode = config[FLASK_TABLE][FLASK_DEBUG]
    endpoint = config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT]
    log_level = config[LOGGER_TABLE][LOGGER_LEVEL]
    ```

Example configuration file:
    ```toml
    [flask]
    debug = true
    secret_key = "your_secret_key"

    [object_storage]
    endpoint = "localhost:9000"
    access_key = "minioadmin"
    secret_key = "minioadmin"
    secure = false

    [logger]
    level = "info"
    ```
"""

from pathlib import Path
from typing import Dict, Any

import os
import toml

from netex.conf.config_parser_constants import *


def load_configs(config_path: Path) -> Dict[str, Any]:
    """
    Load and parse a TOML configuration file, then apply environment variable overrides.

    Args:
        config_path: Path to the TOML configuration file.

    Returns:
        A dictionary containing configuration organized by table (flask, object_storage, logger).

    Raises:
        FileNotFoundError: If the config file does not exist.
        toml.TomlDecodeError: If the config file is malformed.
        ValueError: If required configuration values are missing.
    """
    config = _initialize_config_from_file(config_path)
    _populate_missing_tables(config)
    _update_config_with_env_vars(config)
    _validate_required_config_values(config)

    return config


def _initialize_config_from_file(config_path: Path) -> Dict[Any, Any]:
    """
    Load configuration from a TOML file.

    Args:
        config_path: Path to the TOML configuration file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        toml.TomlDecodeError: If the config file is malformed.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    config = toml.load(config_path)
    print(f"Successfully loaded configuration from {config_path}")

    return config


def _populate_missing_tables(config: Dict[str, Any]) -> None:
    """
    Ensure all required configuration tables exist in the config dictionary.

    Creates empty dictionaries for any missing tables (flask, object_storage, logger).

    Args:
        config: Configuration dictionary to populate.
    """
    if not config.__contains__(FLASK_TABLE):
        config[FLASK_TABLE] = {}
    if not config.__contains__(OBJ_STORE_TABLE):
        config[OBJ_STORE_TABLE] = {}
    if not config.__contains__(LOGGER_TABLE):
        config[LOGGER_TABLE] = {}


def _update_config_with_env_vars(config: Dict[str, Any]) -> None:
    """
    Override configuration values with environment variables if they are set.

    Args:
        config: Configuration dictionary to update.
    """
    if (flask_debug := os.getenv(FLASK_DEBUG_ENV_VAR)) is not None:
        config[FLASK_TABLE][FLASK_DEBUG] = flask_debug.lower() == "true"

    if (flask_key := os.getenv(FLASK_KEY_ENV_VAR)) is not None:
        config[FLASK_TABLE][FLASK_KEY] = flask_key

    if (obj_store_endpoint := os.getenv(OBJ_STORE_ENDPOINT_ENV_VAR)) is not None:
        config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT] = obj_store_endpoint

    if (obj_store_access_key := os.getenv(OBJ_STORE_ACCESS_KEY_ENV_VAR)) is not None:
        config[OBJ_STORE_TABLE][OBJ_STORE_ACCESS_KEY] = obj_store_access_key

    if (obj_store_secret_key := os.getenv(OBJ_STORE_SECRET_KEY_ENV_VAR)) is not None:
        config[OBJ_STORE_TABLE][OBJ_STORE_SECRET_KEY] = obj_store_secret_key

    if (obj_store_secure := os.getenv(OBJ_STORE_SECURE_ENV_VAR)) is not None:
        config[OBJ_STORE_TABLE][OBJ_STORE_SECURE] = obj_store_secure.lower() == "true"

    if (logger_level := os.getenv(LOGGER_LEVEL_ENV_VAR)) is not None:
        config[LOGGER_TABLE][LOGGER_LEVEL] = logger_level


def _validate_required_config_values(config: Dict[str, Any]) -> None:
    """
    Validate that all required configuration values are present.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ValueError: If any required configuration values are missing.
    """
    missing_values = []

    # Flask required values
    if FLASK_DEBUG not in config[FLASK_TABLE]:
        missing_values.append(f"{FLASK_TABLE}.{FLASK_DEBUG}")
    if FLASK_KEY not in config[FLASK_TABLE]:
        missing_values.append(f"{FLASK_TABLE}.{FLASK_KEY}")

    # Object storage required values
    if OBJ_STORE_ENDPOINT not in config[OBJ_STORE_TABLE]:
        missing_values.append(f"{OBJ_STORE_TABLE}.{OBJ_STORE_ENDPOINT}")
    if OBJ_STORE_ACCESS_KEY not in config[OBJ_STORE_TABLE]:
        missing_values.append(f"{OBJ_STORE_TABLE}.{OBJ_STORE_ACCESS_KEY}")
    if OBJ_STORE_SECRET_KEY not in config[OBJ_STORE_TABLE]:
        missing_values.append(f"{OBJ_STORE_TABLE}.{OBJ_STORE_SECRET_KEY}")
    if OBJ_STORE_SECURE not in config[OBJ_STORE_TABLE]:
        missing_values.append(f"{OBJ_STORE_TABLE}.{OBJ_STORE_SECURE}")

    # Logger required values
    if LOGGER_LEVEL not in config[LOGGER_TABLE]:
        missing_values.append(f"{LOGGER_TABLE}.{LOGGER_LEVEL}")

    if missing_values:
        raise ValueError(
            f"Missing required configuration values: {', '.join(missing_values)}"
        )
