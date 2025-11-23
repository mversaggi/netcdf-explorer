import os
import logging
import pathlib

from flask import Flask
from logging.handlers import RotatingFileHandler
from typing import Mapping

templates_directory = pathlib.Path(os.path.join("../../", "templates"))
static_directory = pathlib.Path(os.path.join("../../", "static"))

def create_app(config: Mapping):
    """
    Creates and configures the Flask application instance using the provided config mapping.

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

    # Configure app
    app.logger.debug(f"Using application configuration {config}")

    # Register routes via Flask blueprint
    from routes import app_blueprint

    app.logger.info("Registering server endpoints")
    app.register_blueprint(app_blueprint)

    return app


def configure_logging(app: Flask):
    """
    Configure logging for the Flask application. Attempts to get the log level from a LOG_LEVEL environment variable,
    defaults to INFO if environment variable not set.

    :param app: The Flask app instance to configure logging on
    """

    # Get log level from env-var, default to INFO if env-var invalid or not set
    log_level = logging.getLevelName(os.getenv("LOG_LEVEL"))

    if log_level is None or isinstance(log_level, str):
        log_level = logging.INFO

    app.logger.setLevel(log_level)

    # Clear default handler
    #
    # TODO: Configure logging before creating the Flask app instance to prevent default handler from being added.
    # TODO: See https://flask.palletsprojects.com/en/stable/logging/
    app.logger.handlers.clear()

    # Create and configure formatter
    detailed_formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(levelname)s (%(module)s): %(message)s",
        "%Y-%m-%d, %H:%M:%S"
    )

    # Create and configure console handler for development logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(detailed_formatter)
    app.logger.addHandler(console_handler)

    # Add file handler with rotation for longer-running production deployments, omit during testing
    if not bool(app.config["TESTING"]):
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # Max 10MB per file, keep 10 backup files
        file_handler = RotatingFileHandler(
            "logs/netex.log", maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        app.logger.addHandler(file_handler)


if __name__ == "__main__":
    # TODO: Support environment- and file-based configuration
    app = create_app(
        {
            "FLASK_ENV": "development",
        }
    )
    app.run(debug=True)
