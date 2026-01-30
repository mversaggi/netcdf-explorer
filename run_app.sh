#!/bin/ash

# Exit on any error
set -e

# Run the Flask application
# --host=0.0.0.0 binds to all interfaces, allowing access from outside the container
uv run flask run --host=0.0.0.0
