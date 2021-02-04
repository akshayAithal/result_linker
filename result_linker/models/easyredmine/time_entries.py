#!/usr/bin/env python
# -*- coding: utf-8 -*-

from result_linker.models import db


class TimeEntry(db.Model):
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "time_entries"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(
        "projects.id"), nullable=False)
    project = db.relationship("Project", foreign_keys=project_id)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", foreign_keys=user_id)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"))
    issue = db.relationship("Issue", foreign_keys=issue_id)
    hours = db.Column(db.Float, nullable=False)
    comments = db.Column(db.Text)
    spent_on = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return ("<Time Entry : {} : {} "
                ": {} : {} : {}>").format(self.project_id,
                self.spent_on, self.user.login,
                self.project.name,
                self.issue.subject if self.issue is not None else None)
