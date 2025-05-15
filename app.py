from flask import Flask, redirect, request, render_template, url_for
from netCDF4 import Dataset
from pathlib import Path
import tempfile
import xarray as xr

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            return redirect(url_for("summary", file_path=Path(file)))
    return render_template("index.html.jinja", summary=summary)


@app.get("/summary/<path:file_path>")
def summary(file_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp_file:
                file_path.save(temp_file.name)
                temp_path = temp_file.name

    file_size = Path(file_path).stat().st_size
    ds = xr.open_dataset(temp_path, engine="netcdf4")
    
    summary = str(ds)
    return render_template("index.html.jinja", "summary.html.jinja", file_name=file_path, file_size=file_size, summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
