from io import BytesIO
import humanize
import xarray as xr
from flask import Blueprint, redirect, render_template, request, session, url_for


app_blueprint = Blueprint("netex", __name__)

FILE_SESSION_KEY = "netcdf_file"
FILE_PATH_SESSION_KEY = "netcdf_file_path"


@app_blueprint.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        netcdf_file = request.files["netcdf_file"]
        if netcdf_file:
            # Get file size
            netcdf_file.seek(0, 2)
            file_size = netcdf_file.tell()
            netcdf_file.seek(0, 0)

            # Open the file as a NetCDF dataset
            netcdf_data = xr.open_dataset(BytesIO(netcdf_file.read()))

            # Store the summary text and file size in the session for later use
            session["file_size"] = file_size
            session["summary_text"] = netcdf_data._repr_html_()

            return redirect(
                url_for("netex.summary", netcdf_filename=netcdf_file.filename)
            )

    return render_template("index.html.jinja")


@app_blueprint.get("/summary/<netcdf_filename>")
def summary(netcdf_filename):
    summary = session["summary_text"]
    file_size = session["file_size"]
    return render_template(
        "summary.html.jinja",
        file_name=netcdf_filename,
        file_size=humanize.naturalsize(file_size),
        summary=summary,
    )
