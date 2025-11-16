from flask import Flask


def create_app():
    """
    Creates and configures the Flask application instance. Intended for use by both production and test code.
    """
    app = Flask(__name__)
    # TODO: Secure this before deploying into production
    app.secret_key = "cUrR33_ChI_#"

    # Configure app
    app.config.from_mapping(
        {
            "FLASK_ENV": "development",
        }
    )

    # Register routes via Flask blueprint
    from routes import app_blueprint

    app.register_blueprint(app_blueprint)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
