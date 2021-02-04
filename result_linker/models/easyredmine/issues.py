#!/usr/bin/env python
# -*- coding: utf-8 -*-

from result_linker.models import db


class Issue(db.Model):
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "issues"
    id_ = db.Column("id", db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    project = db.relationship("Project")
    created_on = db.Column(db.DateTime)
    updated_on = db.Column(db.DateTime)
    start_date = db.Column(db.Date)


    def __repr__(self):
        return "<Issue/Task : {} : [{}]>".format(self.id_, self.subject)
