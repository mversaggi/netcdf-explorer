<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/mversaggi/netcdf-explorer">
    <img src="static/blue-block_100x100.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">NetCDF Explorer</h3>

  <p align="center">
    A Flask web application for uploading and analyzing NetCDF3 and NetCDF4 files.
    <br />
    <br />
    <a href="https://github.com/mversaggi/netcdf-explorer/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/mversaggi/netcdf-explorer/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#testing">Testing</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



## About The Project

NetCDF Explorer (netex) is a web application that allows users to upload and analyze NetCDF3 and NetCDF4 files. It
provides a simple interface for viewing file metadata and structure using xarray's HTML representation.

Key features:
* Upload and view NetCDF file summaries including dimensions, coordinates, and variables

<br/>

### Built With

* [![Python][Python-badge]][Python-url]
* [![Flask][Flask-badge]][Flask-url]
* [![Xarray][Xarray-badge]][Xarray-url]
* [![MinIO][MinIO-badge]][MinIO-url]
* [![Tailwind CSS][Tailwind-badge]][Tailwind-url]
* [![Docker][Docker-badge]][Docker-url]

<br/>

### NetCDF Engines

NetCDF Explorer uses [xarray](https://xarray.dev/) to read uploaded files. Since files are streamed from MinIO into memory,
xarray selects a backend engine that supports reading from in-memory buffers. The engine is chosen automatically at runtime
based on the file format:

| File Format | Engine | Notes |
|-------------|--------|-------|
| NetCDF3 (classic) | `scipy` | Handles classic and 64-bit offset NetCDF formats |
| NetCDF4 / HDF5 | `h5netcdf` | Reads HDF5-based NetCDF4 files via `h5py` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

* [Docker](https://docs.docker.com/get-docker/) and Docker Compose (for containerized deployment)
* [uv](https://docs.astral.sh/uv/getting-started/installation/) (for standalone development)
* [Node.js](https://nodejs.org/) (for Tailwind CSS compilation)

### Installation

#### Docker Compose (Recommended)

1. Clone the repo
   ```sh
   git clone https://github.com/mversaggi/netcdf-explorer.git
   cd netcdf-explorer
   ```

2. Start the application with Docker Compose
   ```sh
   docker compose up
   ```

3. Access the application at [http://localhost:5000](http://localhost:5000)

#### Standalone Development

1. Clone the repo
   ```sh
   git clone https://github.com/mversaggi/netcdf-explorer.git
   cd netcdf-explorer
   ```

2. Install Python 3.13 with uv
   ```sh
   uv python install 3.13
   ```

3. Install dependencies
   ```sh
   uv sync
   ```

4. Build Tailwind CSS
   ```sh
   npm install tailwindcss @tailwindcss/cli
   npx @tailwindcss/cli -i ./static/src/input.css -o ./static/dist/output.css
   ```

5. Run the application
   ```sh
   uv run flask --app "src/netex/app:create_app" run
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

1. Navigate to the home page
2. Select a NetCDF file using the file input
3. Click "Explore" to upload the file
4. View the file summary showing dimensions, coordinates, variables, and attributes

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONFIGURATION -->
## Configuration

Configuration is loaded from a TOML file with environment variable overrides. The config file path is specified by the `NETEX_CONFIG` environment variable.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETEX_CONFIG` | Path to TOML config file | Required |
| `FLASK_DEBUG` | Enable Flask debug mode | `false` |
| `FLASK_SECRET_KEY` | Flask session secret key | Required |
| `OBJECT_STORAGE_ENDPOINT` | MinIO server endpoint | Required |
| `OBJECT_STORAGE_ACCESS_KEY` | MinIO access key | Required |
| `OBJECT_STORAGE_SECRET_KEY` | MinIO secret key | Required |
| `OBJECT_STORAGE_SECURE` | Use HTTPS for MinIO | `false` |
| `LOGGER_LEVEL` | Logging level (DEBUG, INFO, etc.) | `INFO` |

### Example Configuration File

```toml
[flask]
debug = true
secret_key = "your_secret_key"

[object_storage]
endpoint = "localhost:9000"
access_key = "minioadmin"
secret_key = "minioadmin"
secure = false

[logger]
level = "info"
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- TESTING -->
## Testing

This project uses pytest for testing.

```sh
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit/

# Run integration tests only (requires Docker for MinIO container)
uv run pytest tests/integration/

# Run with coverage
uv run pytest --cov=src --cov-report=html:tests/reports
```

### Code Formatting

```sh
# Format Python code
uv run black src/ tests/

# Format Jinja2 templates
uv run djlint templates/ --reformat
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] File upload and storage in MinIO
- [ ] Organized summary view of file
- [ ] Variable visualization on globe
- [ ] View saved files


See the [open issues](https://github.com/mversaggi/netcdf-explorer/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/mversaggi/netcdf-explorer](https://github.com/mversaggi/netcdf-explorer)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [xarray](https://xarray.dev/) - N-D labeled arrays and datasets in Python
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) - README template

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Flask-badge]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/
[MinIO-badge]: https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge&logo=minio&logoColor=white
[MinIO-url]: https://min.io/
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Tailwind-badge]: https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white
[Tailwind-url]: https://tailwindcss.com/
[Xarray-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydata/xarray/refs/heads/main/doc/badge.json&style=for-the-badge
[Xarray-url]: https://xarray.dev/
