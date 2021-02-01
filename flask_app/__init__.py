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
db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()


# Import new blueprints
from .users.routes import users
from .groups.routes import groups
from .polls.routes import polls

def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config['MONGODB_HOST'] = "mongodb+srv://dbadmin:iH7nQmjieaSB1eG3@edevore-cluster.vfigo.mongodb.net/quickVote?retryWrites=true&w=majority"
    app.config['SECRET_KEY'] = os.urandom(32)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
   
    # Register new blueprints
    app.register_blueprint(users)
    app.register_blueprint(groups)
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
            '\'unsafe-inline\'',
            '\'unsafe-eval\''
            ],
        'style-src':[
            'https://stackpath.bootstrapcdn.com/bootstrap/',
            '\'unsafe-inline\'',
            '\'unsafe-eval\''
        ]
    }

    Talisman(app, content_security_policy=csp)
    return app
