import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from minio import Minio

from netex.conf.config_parser import load_configs
from netex.conf.config_parser_constants import (
    OBJ_STORE_ENDPOINT,
    OBJ_STORE_TABLE,
    OBJ_STORE_ACCESS_KEY,
    OBJ_STORE_SECRET_KEY,
    OBJ_STORE_SECURE,
    FLASK_TABLE,
    FLASK_DEBUG,
    FLASK_KEY,
)

config_file_env_var = "NETEX_CONFIG"
static_directory = Path(os.path.join("../../", "static"))
templates_directory = Path(os.path.join("../../", "templates"))

NETCDF_BUCKET_NAME = "netcdf-files"


def create_app():
    """
    Creates and configures the Flask application instance using the provided config mapping. This function is called
    directly when `flask --app src/netex/app run` is executed.
    """
    flask_app = Flask(
        __name__, static_folder=static_directory, template_folder=templates_directory
    )

    config_file_path_string = os.environ.get(config_file_env_var)
    if config_file_path_string is None:
        print(f"Config file env-var '{config_file_env_var}' not set, exiting...")

    config_file_path = Path(config_file_path_string)

    # Load config file, allow error to be propagated if raised
    config = load_configs(Path(__file__).parent.parent.parent / config_file_path)
    flask_app.config.update(config)
    debug_config = config[FLASK_TABLE][FLASK_DEBUG]
    if debug_config:
        flask_app.config["TEMPLATES_AUTO_RELOAD"] = True
    flask_app.debug = debug_config

    configure_logging(flask_app)
    flask_app.logger.info("Creating Flask application instance")

    flask_app.secret_key = flask_app.config[FLASK_TABLE][FLASK_KEY]

    flask_app.logger.debug(f"Using application configuration {config}")

    # Connect to MinIO instance
    connect_to_minio(flask_app)

    # Register routes via Flask blueprint
    from .routes import app_blueprint

    flask_app.logger.info("Registering server endpoints")
    flask_app.config["PROVIDE_AUTOMATIC_OPTIONS"] = False
    flask_app.register_blueprint(app_blueprint)

    flask_app.logger.info(f"Successfully created app instance: {flask_app.name}")

    return flask_app


def configure_logging(flask_app: Flask):
    """
    Configure logging for the Flask application. Attempts to get the log level from a LOG_LEVEL environment variable,
    defaults to INFO if environment variable not set.

    :param flask_app: The Flask app instance to configure logging on
    """
    # Get log level from config, default to INFO if invalid or non-existent
    log_level = logging.getLevelName(flask_app.config["logger"]["level"].upper())

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
        "%Y-%m-%d, %H:%M:%S",
    )

    # Create and configure console handler for development logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(detailed_formatter)
    flask_app.logger.addHandler(console_handler)

    # Add file handler with rotation for longer-running production deployments (e.g. netex-1.log, netex-2.log, etc.); omit during testing.
    if not bool(flask_app.config["flask"]["debug"]):
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


def connect_to_minio(app: Flask) -> Minio:
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
    if app is None:
        raise TypeError("Application instance cannot be None")

    app_config = app.config

    endpoint = app_config[OBJ_STORE_TABLE][OBJ_STORE_ENDPOINT]
    access_key = app_config[OBJ_STORE_TABLE][OBJ_STORE_ACCESS_KEY]
    secret_key = app_config[OBJ_STORE_TABLE][OBJ_STORE_SECRET_KEY]
    secure = app_config[OBJ_STORE_TABLE][OBJ_STORE_SECURE]

    app.logger.debug(f"Connecting to MinIO, endpoint={endpoint}")

    # Create MinIO client
    client = Minio(
        endpoint=endpoint, access_key=access_key, secret_key=secret_key, secure=secure
    )

    # Test connection by listing buckets
    buckets = client.list_buckets()

    if buckets is None or len(buckets) == 0:
        app.logger.debug("No buckets found in MinIO instance")
    else:
        app.logger.debug(f"Buckets found in MinIO instance: {buckets}")

    # Create NetCDF bucket if it doesn't exist
    if not client.bucket_exists(NETCDF_BUCKET_NAME):
        client.make_bucket(NETCDF_BUCKET_NAME)
        app.logger.info(f"Created bucket: {NETCDF_BUCKET_NAME}")

    # Store client on app for use in routes
    app.object_store_client = client

    app.logger.info(f"Successfully connected to MinIO at {endpoint}")

    return client


# Example usage for storing NetCDF files
def store_netcdf_example(
    client: Minio, bucket_name: str, file_path: str, object_name: str
):
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
        content_type="application/netcdf",
    )
    print(f"Uploaded {file_path} as {object_name} to bucket {bucket_name}")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["flask"]["debug"])
