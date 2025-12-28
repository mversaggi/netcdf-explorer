#!/bin/ash

# Exit on any error
set -e

# Print environment variables for debugging
echo "Environment variables:"
printenv | sort
echo ""

echo "FLASK_APP=$FLASK_APP \
      FLASK_ENV=$FLASK_ENV \
      FLASK_DEBUG=$FLASK_DEBUG \
      MINIO_ENDPOINT=$MINIO_ENDPOINT \
      MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY \
      MINIO_SECRET_KEY=$MINIO_SECRET_KEY \
      MINIO_SECURE=$MINIO_SECURE \
      NETCDF_BUCKET=$NETCDF_BUCKET" > .netex_config.toml


# Create virtual environment and run netex
uv venv
uv run flask run