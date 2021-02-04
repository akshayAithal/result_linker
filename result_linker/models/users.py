#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from result_linker.extensions import bcrypt
from .db import db
from .user_type import UserType



# pylint: disable=no-member
class User(UserMixin, db.Model):
    """User model for use with flask_login."""
    __tablename__ = "users"
    id_ = db.Column("id", db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # to exist till we have seperate hashed password to svn
    svn_username = db.Column(db.String(255), nullable=False)
    svn_password = db.Column(db.String(255), nullable=False)
    type_ = db.Column("type", db.Enum(UserType), default=UserType.USER)


    def __init__(self, login, password, svn_password, type_, svn_usename = ""):
        """Creates a new user."""
        self.login = login
        if len(svn_usename):
            self.svn_username = svn_usename
        else:
            self.svn_username = login
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')
        self.svn_password = svn_password
        self.type_ = type_

    
    
    def set_svn_username_password(self, svn_username, svn_password):
        self.svn_username = svn_username
        self.svn_password = svn_password

    def check_password(self, password):
        """checks password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def change_password(self, password, svn_password):
        """Change of password in svn"""
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')
        self.svn_password = svn_password

    def change_password(self, password, svn_password):
        """Change of password in svn"""
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')
        self.svn_password = svn_password   


    def get_id(self):
        return self.id_
