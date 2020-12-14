# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_talisman import Talisman

# stdlib
from datetime import datetime
import os

# local
#from .client import MovieClient


db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
#movie_client = MovieClient(os.environ.get("OMDB_API_KEY"))

# Import new blueprints
from .users.routes import users
from .groups.routes import groups
from .polls.routes import polls
from .misc.routes import misc

def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False), 
    #app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    #Talisman(app)

    # Initialize talisman
    #csp = {'default-src': '\'self\''}
    #Talisman(app, content_security_policy=csp)


    # Register new blueprints
    app.register_blueprint(users)
    app.register_blueprint(groups)
    app.register_blueprint(misc)
    app.register_blueprint(polls)

    # Register error handler
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    csp = {
        'default-src': [
            '\'self\'',
            'https://plotly.com/'
        ],
        'script-src':[
            'https://stackpath.bootstrapcdn.com/bootstrap/',
            'https://code.jquery.com/',
            'https://cdnjs.cloudflare.com/ajax/libs/popper.js/',
            ],
        'style-src':[
            'https://stackpath.bootstrapcdn.com/bootstrap/',
        ]
    }

    Talisman(app, content_security_policy=csp)
    return app
