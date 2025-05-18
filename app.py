from io import BytesIO
from flask import Flask, redirect, request, render_template, session, url_for
import humanize
import xarray as xr

app = Flask(__name__)
# TODO: Secure this before deploying into production
app.secret_key = "cUrR33_ChI_#"

FILE_SESSION_KEY = 'netcdf_file'
FILE_PATH_SESSION_KEY = 'netcdf_file_path'

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        netcdf_file = request.files["netcdf_file"]
        if netcdf_file:
            # Open the file as a NetCDF dataset
            netcdf_data = xr.open_dataset(BytesIO(netcdf_file.read()))

            # Get file size
            netcdf_file.seek(0, 2)
            file_size = netcdf_file.tell()
            netcdf_file.seek(0, 0)

            # Store the summary text and file size in the session for later use
            session['summary_text'] = str(netcdf_data)
            session['file_size'] = file_size

            return redirect(url_for("summary", netcdf_filename=netcdf_file.filename))
    return render_template("index.html.jinja")

@app.get("/summary/<netcdf_filename>")
def summary(netcdf_filename):
    summary = session['summary_text']
    file_size = session['file_size']
    return render_template("summary.html.jinja", file_name=netcdf_filename, file_size=humanize.naturalsize(file_size), summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
