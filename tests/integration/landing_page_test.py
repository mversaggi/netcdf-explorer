from flask import url_for, session
from flask_testing import TestCase
from app import app
from werkzeug.datastructures import FileStorage


class TestLandingPage(TestCase):

    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_landing_page_200(self):
        response = self.client.get(url_for("index"))
        self.assert_200(response)

    def test_netcdf_file_posted(self):
        with open('tests/data/sresa1b_ncar_ccsm3-example.nc', 'rb') as netcdf_file:
            test_file = FileStorage(
                stream=netcdf_file,
                filename='sresa1b_ncar_ccsm3-example.nc',
                content_type='application/octet-stream'
            )
        
            with self.client as client:
                response = client.post(url_for("index"), data={"netcdf_file": test_file})
            
                expected_path = url_for("summary", netcdf_filename='sresa1b_ncar_ccsm3-example.nc')
                assert response.location.endswith(expected_path)
                assert 'summary_text' in session
                assert 'file_size' in session

