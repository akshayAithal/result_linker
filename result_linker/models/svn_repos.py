#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from sqlalchemy.dialects.mysql import TINYTEXT, LONGTEXT, TEXT
from .db import db


class SVNRepo(db.Model):
    __tablename__ = "svn_repos"
    id_ = db.Column("id", db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=False)
    project_name = db.Column(db.Text)
    repository_url = db.Column(db.Text)
    jstree_json = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
