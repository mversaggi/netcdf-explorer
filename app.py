from flask import Flask, request, render_template
import tempfile
import xarray as xr
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name
            ds = xr.open_dataset(tmp_path, engine="netcdf4")
            summary = str(ds)
    return render_template("index.html", summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
