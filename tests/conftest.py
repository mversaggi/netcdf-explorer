import os
import sys

import pytest

from netex.app import create_app

# TODO: Explain why this is needed for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="class")
def integration_test_client():
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client
