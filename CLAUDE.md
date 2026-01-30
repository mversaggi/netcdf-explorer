# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NetCDF Explorer (netex) is a Flask web application that allows users to upload and analyze NetCDF3 and NetCDF4 files. It uses MinIO for object storage and xarray for NetCDF data parsing.

## Commands

This project uses **uv** for Python package/interpreter management and running tools.

### Run Tests
```bash
# All tests (pytest auto-discovers from tests/)
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# Integration tests only (requires Docker for MinIO container)
uv run pytest tests/integration/

# Single test file
uv run pytest tests/unit/config_parser_test.py -v

# With coverage
uv run pytest --cov=src --cov-report=html:tests/reports
```

### Run Application
```bash
# Standalone (requires NETEX_CONFIG env var pointing to config file)
export NETEX_CONFIG=tests/conf/netex.toml
uv run flask --app "src/netex/app:create_app" run

# With Docker Compose (includes MinIO)
docker-compose up
```

### Build Tailwind CSS
```bash
npm install tailwindcss @tailwindcss/cli
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css
# Add --watch for development
```

### Format Code
```bash
uv run black src/ tests/
```

## Architecture

### Configuration System
Configuration is loaded via a hierarchical system in `src/netex/conf/`:
- TOML config file (path specified by `NETEX_CONFIG` env var)
- Environment variables override TOML values
- Constants defined in `config_parser_constants.py`

Config tables: `[flask]`, `[object_storage]`, `[logger]`

### Flask App Factory
`src/netex/app.py` contains `create_app()` which:
1. Loads configuration from TOML + env vars
2. Configures logging (console + rotating file handler in production)
3. Connects to MinIO object storage
4. Registers routes via Blueprint from `routes.py`

### Routes
`src/netex/routes.py` defines the Blueprint with:
- `index()`: GET (file upload form) / POST (processes NetCDF file)
- `summary()`: GET (displays xarray HTML representation)

File metadata is stored in Flask session between requests.

### Testing Structure
- `tests/unit/`: Mocked dependencies (MinIO mocked)
- `tests/integration/`: Real MinIO container via testcontainers
- `tests/conf/netex.toml`: Test configuration file
- `tests/data/netcdf/`: Sample NetCDF files for testing

### Frontend
- Jinja2 templates in `templates/`
- Tailwind CSS v4 (input in `static/src/input.css`)

## Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `NETEX_CONFIG` | Path to TOML config file (required) |
| `FLASK_DEBUG` | Enable debug mode |
| `FLASK_SECRET_KEY` | Flask session secret |
| `OBJECT_STORAGE_ENDPOINT` | MinIO endpoint |
| `OBJECT_STORAGE_ACCESS_KEY` | MinIO access key |
| `OBJECT_STORAGE_SECRET_KEY` | MinIO secret key |
| `LOGGER_LEVEL` | Logging level (DEBUG, INFO, etc.) |
