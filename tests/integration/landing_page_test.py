from http import HTTPStatus

from bs4 import BeautifulSoup
from flask import current_app, url_for

from netex.app import NETCDF_BUCKET_NAME


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
        THEN a response code of 302 should be received in the response, redirecting to the summary page.
        """
        test_netcdf_filename = "sresa1b_ncar_ccsm3-example.nc"

        with open(f"tests/data/netcdf/{test_netcdf_filename}", "rb") as netcdf_file:
            response = integration_test_client.post(
                "/",
                data={"netcdf_file": (netcdf_file, test_netcdf_filename)},
            )

            assert response.status_code == HTTPStatus.FOUND

            # Verify file was stored in object storage
            file_stat = current_app.object_store_client.stat_object(
                NETCDF_BUCKET_NAME, test_netcdf_filename
            )
            assert file_stat is not None

            expected_path = url_for(
                "netex.summary", netcdf_filename=test_netcdf_filename
            )
            assert response.location.endswith(expected_path)
