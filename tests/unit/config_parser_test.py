# Add the src directory to the Python path for imports
import os
import sys
import uuid
from pathlib import Path

import pytest
import toml

sys.path.append(str(Path(__file__).parent.parent / "src"))

from netex.conf.config_parser import load_configs
from netex.conf.config_parser_constants import *


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


def test_load_configs_loads_full_config_file(valid_config_path: Path):
    """Test loading a full, valid TOML configuration file."""
    config = load_configs(valid_config_path)

    assert isinstance(config, dict)

    flask_config = config[FLASK_TABLE]
    assert flask_config
    assert flask_config[FLASK_DEBUG] is True
    assert flask_config[OBJ_STORE_SECRET_KEY] == "test_flask_key"

    object_storage_config = config[OBJ_STORE_TABLE]
    assert object_storage_config
    assert object_storage_config[OBJ_STORE_ENDPOINT] == "test_endpoint"
    assert object_storage_config[OBJ_STORE_ACCESS_KEY] == "access_key"
    assert object_storage_config[OBJ_STORE_SECRET_KEY] == "secret_key"
    assert object_storage_config[OBJ_STORE_SECURE] == False

    logger_config = config[LOGGER_TABLE]
    assert logger_config
    assert logger_config[LOGGER_LEVEL] == "debug"


def test_load_configs_uses_env_vars_when_config_file_missing():
    """
    Tests that required configs are still found in environment variables when the application config file can't be found.
    """
    os.environ[OBJ_STORE_ENDPOINT_ENV_VAR] = obj_store_endpoint = uuid.uuid4().__str__()
    os.environ[OBJ_STORE_ACCESS_KEY_ENV_VAR] = obj_store_access_key = (
        uuid.uuid4().__str__()
    )

    config = load_configs(Path("/non/existent/path/config.toml"))

    assert config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT] == obj_store_endpoint
    assert config[OBJ_STORE_TABLE][OBJ_STORE_ACCESS_KEY] == obj_store_access_key


def test_load_configs_returns_empty_dictionary_when_config_file_empty(
    empty_config_path,
):
    """
    Tests that required configs are still found in environment variables when the application config file is empty.
    """
    os.environ[OBJ_STORE_ENDPOINT_ENV_VAR] = obj_store_endpoint = uuid.uuid4().__str__()
    os.environ[OBJ_STORE_ACCESS_KEY_ENV_VAR] = obj_store_access_key = (
        uuid.uuid4().__str__()
    )

    config = load_configs(empty_config_path)

    assert config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT] == obj_store_endpoint
    assert config[OBJ_STORE_TABLE][OBJ_STORE_ACCESS_KEY] == obj_store_access_key


def test_load_configs_raises_toml_decode_error_when_config_is_malformed(
    invalid_config_path,
):
    """
    Tests that required configs are still found in environment variables when the application config file is malformed.
    """
    os.environ[OBJ_STORE_ENDPOINT_ENV_VAR] = obj_store_endpoint = uuid.uuid4().__str__()
    os.environ[OBJ_STORE_ACCESS_KEY_ENV_VAR] = obj_store_access_key = (
        uuid.uuid4().__str__()
    )

    config = load_configs(invalid_config_path)

    assert config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT] == obj_store_endpoint
    assert config[OBJ_STORE_TABLE][OBJ_STORE_ACCESS_KEY] == obj_store_access_key


def test_load_configs_prioritizes_flask_debug_env_var(valid_config_path):
    debug_flag = False
    os.environ[FLASK_DEBUG_ENV_VAR] = debug_flag.__str__()

    config = load_configs(valid_config_path)
    assert config[FLASK_TABLE][FLASK_DEBUG] == debug_flag


def test_load_configs_prioritizes_flask_key_env_var(valid_config_path):
    flask_key = uuid.uuid4().__str__()
    os.environ[FLASK_KEY_ENV_VAR] = flask_key

    config = load_configs(valid_config_path)
    assert config[FLASK_TABLE][FLASK_KEY] == flask_key


def test_load_configs_prioritizes_object_storage_endpoint_env_var(valid_config_path):
    obj_store_endpoint = uuid.uuid4().__str__()
    os.environ[OBJ_STORE_ENDPOINT_ENV_VAR] = obj_store_endpoint

    config = load_configs(valid_config_path)
    assert config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT] == obj_store_endpoint


def test_load_configs_prioritizes_object_storage_access_key_env_var(valid_config_path):
    obj_store_access_key = uuid.uuid4().__str__()
    os.environ[OBJ_STORE_ACCESS_KEY_ENV_VAR] = obj_store_access_key

    config = load_configs(valid_config_path)
    assert config[OBJ_STORE_TABLE][OBJ_STORE_ACCESS_KEY] == obj_store_access_key


def test_load_configs_prioritizes_object_storage_secret_key_env_var(valid_config_path):
    obj_store_secret_key = uuid.uuid4().__str__()
    os.environ[OBJ_STORE_SECRET_KEY_ENV_VAR] = obj_store_secret_key

    config = load_configs(valid_config_path)
    assert config[OBJ_STORE_TABLE][OBJ_STORE_SECRET_KEY] == obj_store_secret_key


def test_load_configs_prioritizes_object_storage_secure_env_var(valid_config_path):
    obj_store_secure_flag = True
    os.environ[OBJ_STORE_SECURE_ENV_VAR] = obj_store_secure_flag.__str__()

    config = load_configs(valid_config_path)
    assert config[OBJ_STORE_TABLE][OBJ_STORE_SECURE] == obj_store_secure_flag


def test_load_configs_prioritizes_logger_level_env_var(valid_config_path):
    logger_level = "warn"
    os.environ[LOGGER_LEVEL_ENV_VAR] = logger_level

    config = load_configs(valid_config_path)
    assert config[LOGGER_TABLE][LOGGER_LEVEL] == logger_level
