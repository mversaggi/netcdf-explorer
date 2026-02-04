from http import HTTPMethod
from io import BytesIO

import humanize
import xarray
from flask import (
    Blueprint,
    current_app,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)
from minio.error import S3Error

from netex.app import NETCDF_BUCKET_NAME

app_blueprint = Blueprint("netex", __name__)


@app_blueprint.route("/", methods=[HTTPMethod.GET, HTTPMethod.POST])
def index():
    if request.method == HTTPMethod.POST:
        netcdf_file = request.files["netcdf_file"]
        current_app.logger.debug(
            f"Received NetCDF summary request for file '{netcdf_file.filename}'"
        )
        if netcdf_file:
            # Get file size
            netcdf_file.seek(0, 2)
            file_size = netcdf_file.tell()
            netcdf_file.seek(0, 0)

            # Upload file to object store
            current_app.object_store_client.put_object(
                bucket_name=NETCDF_BUCKET_NAME,
                object_name=netcdf_file.filename,
                data=netcdf_file,
                length=file_size,
                content_type="application/netcdf",
            )
            current_app.logger.debug(
                f"Uploaded '{netcdf_file.filename}' to bucket '{NETCDF_BUCKET_NAME}'"
            )

            return redirect(
                url_for("netex.summary", netcdf_filename=netcdf_file.filename)
            )

    current_app.logger.debug("Received GET request for index page")
    return render_template("index.html.jinja")


@app_blueprint.get("/summary/<netcdf_filename>")
def summary(netcdf_filename):
    current_app.logger.debug(f"Showing summary for file '{netcdf_filename}'")

    # Retrieve file from object store
    response = None
    try:
        response = current_app.object_store_client.get_object(
            bucket_name=NETCDF_BUCKET_NAME,
            object_name=netcdf_filename,
        )
        file_data = response.read()
        file_size = len(file_data)
    except S3Error as e:
        if e.code == "NoSuchKey":
            current_app.logger.warning(
                f"File '{netcdf_filename}' not found in object store"
            )
            abort(404, description=f"File '{netcdf_filename}' not found")
        raise
    finally:
        if response:
            response.close()
            response.release_conn()

    # Generate summary from NetCDF data
    netcdf_data = xarray.open_dataset(BytesIO(file_data))
    summary_html = netcdf_data._repr_html_()

    return render_template(
        "summary.html.jinja",
        file_name=netcdf_filename,
        file_size=humanize.naturalsize(file_size),
        summary=summary_html,
    )


@app_blueprint.get("/map")
def map_view():
    return render_template("map.html.jinja", heatmap_data=None)
