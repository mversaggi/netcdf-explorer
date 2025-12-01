#!/bin/ash

add_package() {
  package_name=$1
  if ! apk add "$package_name"; then
    echo "Unable to install '" + "$package_name" + "', aborting... "
    exit 1
  fi
}

# Update apk (Alpine Package Keeper)
apk update

# Install Node, NPM, and the HDF5 library
# TODO: Build these into the image instead, to optimize container spin-up
add_package build-base
add_package nodejs-lts
add_package npm
add_package hdf5-dev
add_package netcdf-dev

# Install Tailwind CSS
npm install tailwindcss @tailwindcss/cli
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/src/output.css

# Run the app
uv run flask --app "src/netcdf_explorer/app:create_app({'FLASK_ENV':'development'})" run

