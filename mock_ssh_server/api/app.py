from flask import Flask
import api_routes


def create():
    app = Flask(__name__)
    app.register_blueprint(api_routes.blueprint)
    return app
