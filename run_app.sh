#!/bin/ash

# Exit on any error
set -e

# Install system dependencies
apk update
apk add --no-cache \
    build-base \
    nodejs-lts \
    npm \
    hdf5-dev \
    netcdf-dev

# Install Tailwind CSS
npm install tailwindcss @tailwindcss/cli
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --minify

# Install Python and create a virtual environment
uv python install 3.13
uv venv

# Run the app
uv pip install .
uv run flask --app "src/netcdf_explorer/app:create_app({'FLASK_ENV':'development'})" run