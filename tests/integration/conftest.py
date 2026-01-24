import os
import sys
import uuid

import pytest
from testcontainers.minio import MinioContainer

from netex.app import create_app
from netex.conf.config_parser_constants import (
    OBJ_STORE_ENDPOINT_ENV_VAR,
    OBJ_STORE_ACCESS_KEY_ENV_VAR,
    OBJ_STORE_SECRET_KEY_ENV_VAR,
)

# TODO: Explain why this is needed for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="module")
def minio_container():
    """Start MinIO container for the test session."""

    # Set object store environment variables so that integration tests can connect to the MinIO container
    container_name = "minio-" + uuid.uuid4().__str__()
    access_key = "minioadmin"
    secret_key = "minioadmin123"

    with MinioContainer(
        image="minio/minio:latest-cicd",
        name=container_name,
        access_key=access_key,
        secret_key=secret_key,
    ) as container:
        os.environ[OBJ_STORE_ENDPOINT_ENV_VAR] = (
            "127.0.0.1:" + container.get_exposed_port(9000).__str__()
        )
        os.environ[OBJ_STORE_ACCESS_KEY_ENV_VAR] = access_key
        os.environ[OBJ_STORE_SECRET_KEY_ENV_VAR] = secret_key

        yield container

        # Clean up environment variables
        os.environ.pop(OBJ_STORE_ENDPOINT_ENV_VAR)
        os.environ.pop(OBJ_STORE_ACCESS_KEY_ENV_VAR)
        os.environ.pop(OBJ_STORE_SECRET_KEY_ENV_VAR)


@pytest.fixture(scope="class")
def integration_test_client(minio_container):
    flask_app = create_app()
    flask_app.config["TESTING"] = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client
