#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint,redirect,url_for, session, jsonify, request
from result_linker.models import db
from result_linker.logger import logger
from result_linker.models.share import Share

home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def index(issue_id=0):
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    #logger.info("Its coming here")
    from flask import request
    logger.info(request.headers.get('User-Agent'))
    from flask_login import current_user
    if current_user.is_authenticated:
        logger.info("Authenticated!!")
    else:
        logger.info("Not Authenticated!!")
    logger.debug(session)
    return render_template("index.html")


@home_blueprint.route("/issue/<issue_id>")
def issues(issue_id):
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    share = Share.query.filter_by(issue=issue_id).first()
    if share:
        return redirect(url_for("share.check_share_link",token = share.link))
    session["issue_id"] = issue_id
    return redirect(url_for("home.index"))


@home_blueprint.route("/clear")
def clear(issue_id=0):
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    return jsonify({"success":True})
#@home_blueprint.route("/get_issue")
#def get_issue(issue_id):
#    """Serve the ReactJS-based index.html"""
#    issue_id = session.get("issue_id",0)
#    success_flag=False
#    if issue_id:
#        success_flag = True
#    return jsonify({"success":success_flag,"issue_id": issue_id})