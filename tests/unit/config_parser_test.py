# Add the src directory to the Python path for imports
import sys
from pathlib import Path

import pytest
import toml

sys.path.append(str(Path(__file__).parent.parent / "src"))

from netex.config_parser import load_config


@pytest.fixture
def empty_config_path() -> Path:
    return Path(__file__).parent.parent / "data" / "configs" / "empty_config.toml"


@pytest.fixture
def valid_config_path() -> Path:
    """Gets a reference to the valid config file for testing."""
    return Path(__file__).parent.parent / "data" / "configs" / "valid_config.toml"


@pytest.fixture
def invalid_config_path() -> Path:
    """Gets a reference to the invalid config file for testing."""
    return Path(__file__).parent.parent / "data" / "configs" / "invalid_config.toml"


def test_load_config_raises_file_not_found_error_when_config_does_not_exist():
    """Test loading a non-existent config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("/non/existent/path/config.toml"))


def test_load_config_returns_empty_dictionary_when_config_file_empty(empty_config_path):
    """Test loading an empty config file returns an empty dictionary."""
    assert not load_config(empty_config_path)


def test_load_config_loads_full_config_file(valid_config_path: Path):
    """Test loading a full, valid TOML configuration file."""
    config = load_config(valid_config_path)

    assert isinstance(config, dict)

    flask_config = config["flask"]
    assert flask_config
    assert flask_config["debug"] is True
    assert flask_config["secret_key"] == "test_flask_key"

    object_storage_config = config["object_storage"]
    assert object_storage_config
    assert object_storage_config["endpoint"] == "test_endpoint"
    assert object_storage_config["access_key"] == "access_key"
    assert object_storage_config["secret_key"] == "secret_key"
    assert object_storage_config["secure"] == False

    logger_config = config["logger"]
    assert logger_config
    assert logger_config["level"] == "debug"


def test_load_config_raises_toml_decode_error_when_config_is_malformed(
    invalid_config_path,
):
    """Test loading an invalid TOML file raises TomlDecodeError."""
    with pytest.raises(toml.TomlDecodeError):
        load_config(invalid_config_path)


# def test_get_config_value_simple():
#     """Test getting a simple top-level config value."""
#     config = {"debug": True, "host": "localhost"}
#     assert get_config_value(config, "debug") is True
#     assert get_config_value(config, "host") == "localhost"
#     assert get_config_value(config, "nonexistent", "default") == "default"
#
# def test_get_config_value_nested():
#     """Test getting nested config values using dot notation."""
#     config = {
#         "database": {
#             "host": "localhost",
#             "port": 5432,
#             "credentials": {
#                 "username": "user",
#                 "password": "secret"
#             }
#         }
#     }
#
#     assert get_config_value(config, "database.host") == "localhost"
#     assert get_config_value(config, "database.credentials.username") == "user"
#     assert get_config_value(config, "database.nonexistent", "default") == "default"
#     assert get_config_value(config, "nonexistent.key") is None
#
# def test_get_config_value_edge_cases():
#     """Test edge cases for get_config_value."""
#     config = {
#         "empty": {},
#         "none_value": None,
#         "nested": {"empty_dict": {}, "none_value": None}
#     }
#
#     assert get_config_value({}, "any.key") is None
#     assert get_config_value(config, "empty") == {}
#     assert get_config_value(config, "none_value") is None
#     assert get_config_value(config, "nested.empty_dict") == {}
#     assert get_config_value(config, "nested.none_value") is None
#     assert get_config_value(config, "nested.nonexistent", []) == []
#
# def test_load_config_default_path(monkeypatch):
#     """Test that load_config uses default path when none is provided."""
#     mock_data = {"test": "value"}
#
#     with patch('toml.load', return_value=mock_data) as mock_load:
#         with patch('pathlib.Path.exists', return_value=True):
#             config = load_config()
#
#     mock_load.assert_called_once()
#     assert config == mock_data
#
# def test_get_config_value_with_none_config():
#     """Test get_config_value handles None config gracefully."""
#     assert get_config_value(None, "any.key") is None
#     assert get_config_value(None, "any.key", "default") == "default"
