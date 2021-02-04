#!/usr/bin/env python
# -*- coding: utf-8 -*-

from result_linker.models import db


class Project(db.Model):
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "projects"
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    easy_is_easy_template = db.Column(db.Integer)

    def __repr__(self):
        return '<Project : {} : [{}]>'.format(self.name, self.id)
