from flask import Flask, request, render_template
import xarray as xr
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            ds = xr.open_dataset(file)
            summary = str(ds)
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)