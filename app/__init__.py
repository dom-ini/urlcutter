import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_mongoengine import MongoEngine

from config import Config

db = MongoEngine()
login_manager = LoginManager()
login_manager.login_view = "auth.login_view"
login_manager.login_message = "Please log in to access this page."
mail = Mail()
moment = Moment()


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    if not app.debug and not app.testing:
        if app.config["LOG_TO_STDOUT"]:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)

        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            log_file_handler = RotatingFileHandler("logs/site.log", maxBytes=10240, backupCount=10)
            log_file_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
            )
            log_file_handler.setLevel(logging.INFO)
            app.logger.addHandler(log_file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Site startup")

    return app


from app import models
