#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from .db import db


class Mapping(db.Model):
    """Mappings table class definition."""
    # pylint: disable=no-member
    __bind_key__ = "svn_linker"
    __tablename__ = "mappings"
    issue = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500), nullable=False)
    user = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, issue, link, user):
        self.user = user
        self.issue = issue
        self.link = link

    def __repr__(self):
        """Raw representation."""
        return (
            "<Mapping(issue='{}', "
            "link='{}', "
            "user='{}', "
            "timestamp='{}'>").format(
                self.issue, self.link,
                self.user, self.timestamp)

    def get_dict(self):
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())

    @staticmethod
    def get_all_mappings():
        """Utility function to retrieve all mappings."""
        return Mapping.query.all()

    @staticmethod
    def get_mapped_issue(link):
        """Utility function to retrieve all mappings."""
        mapped_issue_list = []
        mapped_list_1 = Mapping.query.filter_by(link=link).all()
        mapped_issue_list.extend(mapped_list_1)
        ip_link = link.replace("dllohsr222","10.133.0.222")
        mapped_list_2 = Mapping.query.filter_by(link=ip_link).all()
        mapped_issue_list.extend(mapped_list_2)
        if link.endswith("/"):
            link =  link[:-1]
            mapped_list_3 = Mapping.query.filter_by(link=link).all()
            mapped_issue_list.extend(mapped_list_3)
            ip_link = link.replace("dllohsr222","10.133.0.222")
            mapped_list_4 = Mapping.query.filter_by(link=ip_link).all()
            mapped_issue_list.extend(mapped_list_4)
        else:
            link =  link + "/"
            mapped_list_3 = Mapping.query.filter_by(link=link).all()
            mapped_issue_list.extend(mapped_list_3)
            ip_link = link.replace("dllohsr222","10.133.0.222")
            mapped_list_4 = Mapping.query.filter_by(link=ip_link).all()
            mapped_issue_list.extend(mapped_list_4)
        return mapped_issue_list


    @staticmethod
    def get_mapping_for(issue):
        """Utility function to retrieve the mapping for a specific issue id."""
        return Mapping.query.filter_by(issue=issue).first()

    @staticmethod
    def map(issue, link, user):
        """Utility function to map a url to a redmine issue number."""
        mapping = Mapping.query.filter_by(issue=issue).first()
        if mapping:
            mapping.link = link
            mapping.user = user
            mapping.timestamp = datetime.datetime.utcnow()
        else:
            mapping = Mapping(issue=issue, link=link, user=user)
            db.session.add(mapping)
        db.session.commit()
