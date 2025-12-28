from http import HTTPStatus

from bs4 import BeautifulSoup
from flask import url_for, session


class TestLandingPage:
    """
    Integration test suite for the NetCDF Explorer landing page.
    """

    def test_landing_page(self, integration_test_client):
        """
        GIVEN a correctly configured Flask app
        WHEN a GET request is sent to the index route
        THEN a response code of 200 should be received in the response, and the page should contain the application
            title, logo, file input, and submit button.
        """
        response = integration_test_client.get("/")
        assert response.status_code == HTTPStatus.OK

        # Validate title is present and correct in metadata
        html = BeautifulSoup(response.data, "html.parser")
        assert html.title.string == "NetCDF Explorer"

        # Validate application title and logo are present on the page
        assert html.span
        assert html.span.string == "NetCDF Explorer"
        assert html.img
        assert html.img["src"] == url_for("static", filename="blue-block_100x100.png")

        # Validate submit button and file input are present
        assert html.button
        assert html.button["type"] == "submit"
        assert html.input
        assert html.input["type"] == "file"

    def test_netcdf_file_posted(self, integration_test_client):
        """
        GIVEN the NetCDF Explorer landing page
        WHEN a POST request is sent to the index route with a valid NetCDF file
        THEN a response code of 302 should be received in the response, and the session should contain summary text and
            the file size.
        """
        test_netcdf_filename = "sresa1b_ncar_ccsm3-example.nc"

        with open(f"tests/data/{test_netcdf_filename}", "rb") as netcdf_file:
            response = integration_test_client.post(
                "/",
                data={"netcdf_file": (netcdf_file, test_netcdf_filename)},
            )

            assert response.status_code == HTTPStatus.FOUND

            expected_path = url_for(
                "netex.summary", netcdf_filename=test_netcdf_filename
            )
            assert response.location.endswith(expected_path)
            assert "summary_text" in session
            assert session["summary_text"] is not None
            assert "file_size" in session
            assert session["file_size"] == 2_767_916
