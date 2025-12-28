from http import HTTPMethod

import pytest

from netex.app import create_app


class TestApp:
    """
    Unit test suite for the NetCDF Explorer app.
    """

    @pytest.fixture()
    def mocked_database_app(self, mocker):
        """ """
        # Mock the Minio class where it's imported in your module
        mock_minio_class = mocker.patch("netex.app.Minio")

        # Configure mock Minio instance for unit testing
        mock_minio_instance = mock_minio_class.return_value
        mock_minio_instance.list_buckets().return_value = []

        # Now call create_app
        yield create_app()

        # Code that will run after your test, for example:

    #        files_after = # ... do something to check the existing files
    #        assert files_before == files_after

    def test_app_contains_index_route(self, mocked_database_app):
        """
        WHEN create_app() is called
        THEN a Flask app with an index route ("/") supporting GET and POST methods should be returned.
        """
        # Assert configs
        assert mocked_database_app is not None
        assert mocked_database_app.secret_key is not None

        url_map = mocked_database_app.url_map
        # Assert index route is registered and supports GET and POST methods
        routes = [rule for rule in url_map.iter_rules() if rule.rule == "/"]
        assert len(routes) == 1
        index_rule = routes[0]

        assert index_rule.rule == "/"

        assert HTTPMethod.GET in index_rule.methods
        assert HTTPMethod.POST in index_rule.methods

    def test_app_contains_summary_route(self, mocked_database_app):
        """
        WHEN create_app() is called
        THEN a Flask app with a /summary/{netcdf_filename} route supporting only the GET method should be returned.
        """
        url_map = mocked_database_app.url_map
        # Assert summary route is registered and supports GET method
        routes = [
            rule
            for rule in url_map.iter_rules()
            if rule.rule == "/summary/<netcdf_filename>"
        ]
        assert len(routes) == 1
        summary_rule = routes[0]

        assert summary_rule.rule == "/summary/<netcdf_filename>"
        assert HTTPMethod.GET in summary_rule.methods
