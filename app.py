import os
import logging

from flask import Flask
from logging.handlers import RotatingFileHandler
from typing import Mapping


def create_app(config: Mapping):
    """
    Creates and configures the Flask application instance using the provided config mapping.
    """
    app = Flask(__name__)

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
    """

    # Get log level from env-var, default to INFO if env-var invalid or not set
    log_level = logging.getLevelName(os.getenv("LOG_LEVEL"))

    if log_level is None or isinstance(log_level, str):
        log_level = logging.INFO

    app.logger.setLevel(log_level)

    # Remove default Flask handlers to avoid duplicate logs
    app.logger.handlers.clear()

    # Create and configure formatter
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s", "%H:%M:%S,%f %Y-%m-%d"
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
