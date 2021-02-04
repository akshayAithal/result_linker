#!/usr/bin/env python
# -*- coding: utf-8 -*-

from result_linker.models import db


class Repository(db.Model):
    __bind_key__ = "easyredmine"
    __tablename__ = "repositories"
    id_ = db.Column("id", db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    url = db.Column(db.String(255), nullable=False)
