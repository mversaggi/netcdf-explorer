import os
import logging
import pathlib

from flask import Flask
from logging.handlers import RotatingFileHandler
from minio import Minio
from typing import Dict, Mapping

templates_directory = pathlib.Path(os.path.join("../../", "templates"))
static_directory = pathlib.Path(os.path.join("../../", "static"))

def create_app(config: Mapping):
    """
    Creates and configures the Flask application instance using the provided config mapping. This function is called
    directly when `flask --app src/netcdf-explorer/app run` is executed.

    :param config: The config mapping containing configuration key-value pairs
    """
    app = Flask(__name__,
                static_folder=static_directory,
                template_folder=templates_directory)

    app.config.from_mapping(config)
    configure_logging(app)
    app.logger.info("Creating Flask application instance")

    # TODO: Secure this before deploying into production
    app.secret_key = "cUrR33_ChI_#"

    app.logger.debug(f"Using application configuration {config}")

    # Connect to MinIO instance
    connect_to_minio(app.config)

    # Register routes via Flask blueprint
    from .routes import app_blueprint

    app.logger.info("Registering server endpoints")
    app.register_blueprint(app_blueprint)

    app.logger.info(f"Successfully created app instance: {app.name}")

    return app


def configure_logging(flask_app: Flask):
    """
    Configure logging for the Flask application. Attempts to get the log level from a LOG_LEVEL environment variable,
    defaults to INFO if environment variable not set.

    :param flask_app: The Flask app instance to configure logging on
    """

    # Get log level from env-var, default to INFO if env-var invalid or not set
    log_level = logging.getLevelName(os.getenv("LOG_LEVEL"))

    if log_level is None or isinstance(log_level, str):
        log_level = logging.INFO

    flask_app.logger.setLevel(log_level)

    # Clear default handler
    #
    # TODO: Configure logging before creating the Flask app instance to prevent default handler from being added.
    # TODO: See https://flask.palletsprojects.com/en/stable/logging/
    flask_app.logger.handlers.clear()

    # Create and configure formatter
    detailed_formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(levelname)s (%(module)s): %(message)s",
        "%Y-%m-%d, %H:%M:%S"
    )

    # Create and configure console handler for development logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(detailed_formatter)
    flask_app.logger.addHandler(console_handler)

    # Add file handler with rotation for longer-running production deployments (e.g. netex-1.log, netex-2.log, etc.); omit during testing.
    if not bool(flask_app.config["TESTING"]):
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # Max 10MB per file, keep 10 backup files
        file_handler = RotatingFileHandler(
            "logs/netex.log", maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        flask_app.logger.addHandler(file_handler)

def connect_to_minio(
    app_config: Dict[str, str] = None
) -> Minio:
    """
    Creates and configures a connection to a MinIO instance for storage of NetCDF files. The given config dictionary
    is first checked for connection parameters; default values are used where no config parameter is provided. 
    
    TODO: Secure database connection
    
    Args:
        config: Dictionary containing MinIO connection parameters.
                Supported keys:
                - endpoint: MinIO server endpoint (default: "localhost:9000")
                - access_key: Access key ID (default: "minioadmin")
                - secret_key: Secret access key (default: "minioadmin")
    
    Returns:
        Minio: Connected MinIO client instance
        
    Example:
        >>> config = {
        ...     "endpoint": "minio.netex.com:9000",
        ...     "access_key": "my_access_key",
        ...     "secret_key": "my_secret_key",
        ... }
        >>> client = connect_to_minio(app.config)
    """

    if app_config is None:
        raise TypeError("Application configuration cannot be None")

    host = app_config.get("HOST", "localhost:9000")
    access_key = app_config.get("ACCESS_KEY", "minioadmin")
    secret_key = app_config.get("SECRET_KEY", "minioadmin")

    # Create MinIO client
    client = Minio(
        endpoint=host,
        access_key=access_key,
        secret_key=secret_key,
    )
    
    # Test connection by listing buckets
    buckets = client.list_buckets()

    if (buckets is None or len(buckets) == 0):
        app.logger.debug("No buckets found in MinIO instance")
    else:
        app.logger.debug(f"Buckets found in MinIO instance: {client.list_buckets()}")

    app.logger.info(f"Successfully connected to MinIO at {host}")
    
    return client


# Example usage for storing NetCDF files
def store_netcdf_example(client: Minio, bucket_name: str, file_path: str, object_name: str):
    """
    Example function to store a NetCDF file in MinIO.
    
    Args:
        client: Connected MinIO client
        bucket_name: Name of the bucket to store the file in
        file_path: Local path to the NetCDF file
        object_name: Name for the object in MinIO
    """
    # Create bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")
    
    # Upload NetCDF file
    client.fput_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file_path,
        content_type="application/netcdf"
    )
    print(f"Uploaded {file_path} as {object_name} to bucket {bucket_name}")


if __name__ == "__main__":
    # TODO: Support environment- and file-based configuration
    app = create_app(
        {
            "FLASK_ENV": "development",
        }
    )
    app.run(debug=True)
