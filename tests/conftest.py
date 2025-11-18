import sys
import os
import pytest

from app import create_app
from tests import constants

# TODO: Explain why this is needed for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="class")
def test_client():
    flask_app = create_app(
        {"FLASK_ENV": "development", "TESTING": constants.SET_TESTING_CONFIG}
    )

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client
