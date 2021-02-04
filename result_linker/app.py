#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""result_linker application server definition."""

# pylint: disable=no-member

import os
import warnings

from flask import Flask
from flask_apscheduler import APScheduler

# from flask_restful import Api, Resource  # Implement OpenAPI/Swagger definitions

from flask_migrate import Migrate

# TODO: Use the gkn library instead.

from result_linker.logger import install_logger, logger

from result_linker.extensions import bcrypt
from result_linker.extensions import login_manager
from result_linker.extensions import scheduler
from result_linker.extensions import migrate
from result_linker.extensions import jwt
from result_linker.models import db

def create_app(config_filename=None, config=None):
    """Application factory function that returns the flask app
    with the configs loaded correctly.
    
    For secret key, use os.urandom(32). Don't put the function into the file.
    Open an interpreter, calculate this value and put that value into the file
    as a string.

    Protip: If something does not work, try accessing this in incognito mode.

    Args:
        config_filename: Path to a config file. This can be
            relative to the instance folder.
        config: This is the name of one of the configs that should be loaded.
            This is loaded from the config file. Example: config='test' will
            load test.py

    """
    #logger.debug("config_filename = {}".format(config_filename))
    #logger.debug("config_filename = {}".format(config))
    app = Flask(
        __name__,
        static_folder="ui/assets",
        template_folder="ui",
        instance_relative_config=True)
    #if config:
    #    app.config.from_object(config)
    #else:
    #    app.config.from_object("config.default")

    if config_filename:
        app.config.from_pyfile(config_filename)
    else:
        if os.environ.get("RESULTLINKER_CFG"):
            app.config.from_envvar("RESULTLINKER_CFG")
        else:
            warnings.warn(
                "Either set the RESULTLINKER_CFG environment variable"
                "or provide the config_filename argument to the "
                "application factory function. The default configuration "
                "has been used, but the changes to the database are "
                "now stored in memory, which is not recommended.",
                UserWarning)
    logger.debug("SQLALCHEMY_DATABASE_URI = {}".format(
    app.config["SQLALCHEMY_DATABASE_URI"]))
    bcrypt.init_app(app)
    install_logger(app)
    db.init_app(app)
    migrate.init_app(app, db=db)
    jwt.init_app(app)
    from result_linker.models.users import User
    login_manager.init_app(app)
    login_manager.session_protection = "strong"
    login_manager.login_view = "user.login"
    
    @login_manager.user_loader
    def load_user(user_id):
        """User Loader function for the login manager
        # ? does this go here
        """
        logger.debug(f"Attempting to load user #{user_id}")
        return User.query.filter(User.id_==user_id).first()

    from result_linker.api import home_blueprint
    from result_linker.api import user_blueprint 
    from result_linker.api import svn_blueprint
    from result_linker.api import download_blueprint       
    from result_linker.api import share_blueprint    
    from result_linker.api import link_blueprint   
    from result_linker.api import write_blueprint   
    app.register_blueprint(user_blueprint)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(svn_blueprint,url_prefix="/results")
    app.register_blueprint(download_blueprint,url_prefix="/download")
    app.register_blueprint(share_blueprint,url_prefix="/share")
    app.register_blueprint(link_blueprint,url_prefix="/link")
    app.register_blueprint(write_blueprint,url_prefix="/write")
    return app
