from app import create_app
from http import HTTPMethod


class TestApp:
    """
    Unit test suite for the NetCDF Explorer app.
    """

    def test_app_contains_index_route(self):
        """
        WHEN create_app() is called
        THEN a Flask app with an index route ("/") supporting GET and POST methods should be returned.
        """
        app = create_app()

        # Assert configs
        assert app is not None
        assert app.config["FLASK_ENV"] == "development"
        assert app.secret_key is not None

        url_map = app.url_map
        # Assert index route is registered and supports GET and POST methods
        routes = [rule for rule in url_map.iter_rules() if rule.rule == "/"]
        assert len(routes) == 1
        index_rule = routes[0]

        assert index_rule.rule == "/"
        
        assert HTTPMethod.GET in index_rule.methods
        assert HTTPMethod.POST in index_rule.methods

    def test_app_contains_summary_route(self):
        """
        WHEN create_app() is called
        THEN a Flask app with a "/summary/{netcdf_filename} route supporting only the GET method should be returned.
        """
        app = create_app()

        url_map = app.url_map
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
