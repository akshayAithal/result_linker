#!/usr/bin/env python
# -*- coding: utf-8 -*-

from result_linker.models import db

from result_linker.models.easyredmine.time_entries import TimeEntry
from result_linker.models.easyredmine.custom_values import CustomValue


class User(db.Model):
    """Class for the users table."""
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "users"
    id_ = db.Column("id", db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    type_ = db.column("type", db.String(255))
    groups = db.relationship(
        "Groups_User",
        primaryjoin="Groups_User.user_id == User.id")

    def __repr__(self):
        return "<User : {}, {} [{}:{}]>".format(
            self.lastname, self.firstname, self.id, self.login)

    def get_time_entries(self):
        return db.session.query(TimeEntry).filter(
            TimeEntry.user_id == self.id_).all()

    def get_groups(self):
        return [group.group for group in self.groups]
