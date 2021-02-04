#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import warnings

from flask import Blueprint, abort, flash, redirect,url_for
from flask import request, render_template, jsonify, session
from flask_login import login_required, current_user, login_user
from flask import current_app
from result_linker.models.users import User
import svnlib
from result_linker.models import db
from result_linker.logger import logger
from result_linker.models.mappings import Mapping
from result_linker.utils.svn_utils import (get_icons, get_folder_with_all_children_and_root,get_redmine_session,write_public_data_for_given_links)
from result_linker.models.share import Share
write_blueprint = Blueprint("write", __name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from result_linker.models.easyredmine.base import Base
from result_linker.models.easyredmine.custom_values import CustomValue
from result_linker.models.easyredmine.custom_fields import CustomField


@write_blueprint.route("/",methods=["GET", "POST"])
@login_required
def write_to_svn():
    """API to link the ticket with the repostiory data."""
    import jwt
    import datetime
    from result_linker.utils.rest_utilities import load_request_data
    if request.method == "POST":
        data = load_request_data(request)
        issue_id = data["issue_id"]
        issues = []
        # Need to be cleaned up
        if "," in issue_id:
            issues= issue_id.split(issue_id)
            for issue in issues:
                issue_id = issue
                selected_data = data["data"]
                #logger.debug(selected_data)
                final_links = []
                selected_links = []
                for obj  in selected_data:
                    link = obj.get("svn_link")
                    selected_links.append(link)
                for obj  in selected_data:
                    parent = obj.get("parent")
                    if parent not in selected_links:
                        final_links.append(obj.get("svn_link"))
                write_public_data_for_given_links(issue_id, final_links)
        else:
            selected_data = data["data"]
            #logger.debug(selected_data)
            final_links = []
            selected_links = []
            for obj  in selected_data:
                link = obj.get("svn_link")
                selected_links.append(link)
            for obj  in selected_data:
                parent = obj.get("parent")
                if parent not in selected_links:
                    final_links.append(obj.get("svn_link"))
            write_public_data_for_given_links(issue_id, final_links)
        return jsonify({"success":True})
    return jsonify({"success":True})