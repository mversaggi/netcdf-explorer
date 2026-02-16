# TODO: Reduce image size, see https://mversagg.atlassian.net/browse/NEX-11

FROM ghcr.io/astral-sh/uv:alpine3.22

# Install system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    nodejs-lts \
    npm \
    hdf5-dev

# Set working directory
WORKDIR /app

# Copy src, static, template, and conf directories
COPY ./src ./src
COPY ./static ./static
COPY ./templates ./templates
COPY ./conf ./conf

# Copy package files
COPY package*.json .
COPY uv.lock .

# Copy python build files
COPY ./pyproject.toml .
COPY ./.python-version .

# Copy run script
COPY ./run_app.sh .

# Install Node.js dependencies and build Tailwind CSS
RUN npm install tailwindcss @tailwindcss/cli && \
    npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --minify

# Install Python
RUN uv python install 3.13

# Install Python dependencies
RUN uv venv
RUN uv pip install -e .

# Make the entrypoint script executable
RUN chmod +x run_app.sh

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["./run_app.sh"]