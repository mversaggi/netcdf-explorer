from bs4 import BeautifulSoup
from flask import url_for, session
from flask_testing import TestCase
from app import app
from werkzeug.datastructures import FileStorage


class TestLandingPage(TestCase):
    """
        Integration test suite for the NetCDF Explorer landing page.
    """

    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_landing_page(self):
        """
        GIVEN the NetCDF Explorer landing page
        WHEN a GET request is sent to the index route
        THEN a response code of 200 should be received in the response, and the page should contain the application
             title, logo, file input, and submit button.
        """
        response = self.client.get(url_for("index"))
        self.assert_200(response)

        # Validate title is present and correct in metadata
        html = BeautifulSoup(response.data, 'html.parser')
        assert html.title.string == "NetCDF Explorer"

        # Validate application title and logo are present on the page
        assert html.span
        assert html.span.string == "NetCDF Explorer"
        assert html.img
        assert html.img['src'] == url_for('static', filename='blue-block_100x100.png')

        # Validate submit button and file input are present
        assert html.button
        assert html.button['type'] == 'submit'
        assert html.input
        assert html.input['type'] == 'file'
        

    def test_netcdf_file_posted(self):
        """
        GIVEN the NetCDF Explorer landing page
        WHEN a POST request is sent to the index route with a valid NetCDF file
        THEN a response code of 302 should be received in the response, and the session should contain summary text and
             the file size.
        """
        with open('tests/data/sresa1b_ncar_ccsm3-example.nc', 'rb') as netcdf_file:
            test_file = FileStorage(
                stream=netcdf_file,
                filename='sresa1b_ncar_ccsm3-example.nc',
                content_type='application/octet-stream'
            )
        
            with self.client as client:
                response = client.post(url_for("index"), data={"netcdf_file": test_file})
                assert response.status_code == 302
            
                expected_path = url_for("summary", netcdf_filename='sresa1b_ncar_ccsm3-example.nc')
                assert response.location.endswith(expected_path)
                assert 'summary_text' in session
                assert session['summary_text'] is not None
                assert 'file_size' in session
                assert session['file_size'] == 2_767_916



