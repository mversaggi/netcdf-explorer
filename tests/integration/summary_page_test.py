import humanize

from bs4 import BeautifulSoup
from flask import session
from http import HTTPStatus


class TestSummaryPage:
    """
    Integration test suite for the NetCDF Explorer summary page.
    """

    def test_summary_page(self, test_client):
        """
        GIVEN a POST request is sent to the index route with a valid NetCDF file
        WHEN a 302 redirect response is received and followed to the summary endpoint
        THEN a page summarizing the NetCDF file should be displayed to the user.
        """
        test_netcdf_filename = "sresa1b_ncar_ccsm3-example.nc"

        with open(f"tests/data/{test_netcdf_filename}", "rb") as netcdf_file:
            post_index_response = test_client.post(
                "/",
                data={"netcdf_file": (netcdf_file, test_netcdf_filename)},
            )

            assert post_index_response.status_code == HTTPStatus.FOUND

            get_summary_response = test_client.get(post_index_response.location)

            # Validate summary block and title are present
            html = BeautifulSoup(get_summary_response.data, "html.parser")
            summary_div = html.find("div", id="summary")
            assert summary_div
            assert (
                summary_div.h1.string
                == f"{test_netcdf_filename} ({humanize.naturalsize(session['file_size'])})"
            )

            # Validate summary string is correct
            summary_details = summary_div.pre
            assert summary_details
            assert len(summary_details.contents) > 0
            assert str(next(summary_details.children)) == str(
                BeautifulSoup(session["summary_text"], "html.parser")
            )
