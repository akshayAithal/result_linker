#!/usr/bin/env python
# -*- coding: utf-8 -*-


import click
from flask_script import Manager
from flask_migrate import MigrateCommand

from result_linker.app import db
from result_linker.logger import logger
from result_linker.app import create_app
from result_linker.models.users import User
from result_linker .models.user_type import UserType

manager = Manager(create_app)

manager.add_option("-c", "--config", dest="config_filename", required=False)

manager.add_command("db", MigrateCommand)


@manager.command
@manager.option(dest="user", help="User account", required=True)
@manager.option(dest="password", required=False)
@manager.option(dest="user_type", required=False)
@manager.option(dest="svnusername", required=False)
@manager.option(dest="svnpassword", required=False)
def add_user(user, password, user_type, svnusername,svnpassword):
    """Add user.
    python manage.py -c config.py add_user user1
    python manage.py -c config.py add_user user1 password
    python manage.py -c config.py add_user user2 password admin
    """
    old_user = User.query.filter_by(login=user).first()
    if not old_user:
        logger.info("Creating {} account!".format(user))
        if  user_type.lower() == "guest":
            user_type = UserType.GUEST
        elif user_type.lower() != "admin":
            user_type = UserType.USER
        else:
            user_type = UserType.ADMIN
        from result_linker.app import bcrypt
        user = User(login=user, password=password, type_=user_type)
        user.set_svn_username_password(svnusername,svnpassword)
        db.session.add(user)
        db.session.commit()
    else:
        logger.warning("User already exists. Please use \"modify_user\" command to modify the user")

@manager.command
@manager.option(dest="user", help="User account", required=True)
def delete_user(user):
    """Delete User user.
    python manage.py -c config.py delete_user user1
    """
    old_user = User.query.filter_by(login=user).first()
    if old_user:
        db.session.delete(old_user)
        db.session.commit()
    else:
        logger.warning("No user to delete!!")

if __name__ == "__main__":
    manager.run()