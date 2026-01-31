from http import HTTPStatus

import humanize
from bs4 import BeautifulSoup
from flask import current_app

from netex.app import NETCDF_BUCKET_NAME


class TestSummaryPage:
    """
    Integration test suite for the NetCDF Explorer summary page.
    """

    def test_summary_page(self, integration_test_client):
        """
        GIVEN a POST request is sent to the index route with a valid NetCDF file
        WHEN a 302 redirect response is received and followed to the summary endpoint
        THEN a page summarizing the NetCDF file should be displayed to the user,
            with the summary generated from the file stored in MinIO.
        """
        test_netcdf_filename = "sresa1b_ncar_ccsm3-example.nc"

        with open(f"tests/data/netcdf/{test_netcdf_filename}", "rb") as netcdf_file:
            # Get original file size for comparison
            netcdf_file.seek(0, 2)
            expected_file_size = netcdf_file.tell()
            netcdf_file.seek(0, 0)

            post_index_response = integration_test_client.post(
                "/",
                data={"netcdf_file": (netcdf_file, test_netcdf_filename)},
            )

            assert post_index_response.status_code == HTTPStatus.FOUND

            # Verify file was stored in object storage
            file_stat = current_app.object_store_client.stat_object(
                NETCDF_BUCKET_NAME, test_netcdf_filename
            )
            assert file_stat is not None
            assert file_stat.size == expected_file_size

            get_summary_response = integration_test_client.get(
                post_index_response.location
            )

            assert get_summary_response.status_code == HTTPStatus.OK

            # Validate summary block and title are present
            html = BeautifulSoup(get_summary_response.data, "html.parser")
            summary_div = html.find("div", id="summary")
            assert summary_div
            # Normalize whitespace to handle template formatting differences
            h1_text = " ".join(summary_div.h1.get_text().split())
            assert (
                h1_text
                == f"{test_netcdf_filename} ({humanize.naturalsize(expected_file_size)})"
            )

            # Validate summary content is present (xarray HTML representation)
            summary_details = summary_div.pre
            assert summary_details
            assert len(summary_details.contents) > 0

    def test_summary_page_file_not_found(self, integration_test_client):
        """
        GIVEN a GET request is sent to the summary route with a filename that doesn't exist in MinIO
        WHEN the summary endpoint attempts to retrieve the file
        THEN a 404 response should be returned with a helpful error message.
        """
        non_existent_filename = "non_existent_file.nc"

        response = integration_test_client.get(f"/summary/{non_existent_filename}")

        assert response.status_code == HTTPStatus.NOT_FOUND
