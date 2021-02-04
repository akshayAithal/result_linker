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
from result_linker.utils.svn_utils import (get_icons, get_folder_with_all_children_and_root,get_redmine_session)
from result_linker.models.share import Share
link_blueprint = Blueprint("link", __name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from result_linker.models.easyredmine.base import Base
from result_linker.models.easyredmine.custom_values import CustomValue
from result_linker.models.easyredmine.custom_fields import CustomField

def get_repostitory_field_id(session):
    custom_field = session.query(CustomField).filter(
        CustomField.type_ == "IssueCustomField",
        CustomField.name == "Link To Results").first()
    return custom_field.id_

@link_blueprint.route("/",methods=["GET", "POST"])
@login_required
def link_to_ticket():
    """API to link the ticket with the repostiory data."""
    import jwt
    import datetime
    from result_linker.utils.rest_utilities import load_request_data
    if request.method == "POST":
        data = load_request_data(request)
        logger.info(data)
        issue_id = data["issue_id"]
        issues = []
        # Need to be cleaned up
        if "," in issue_id:
            issues= issue_id.split(issue_id)
            for issue in issues:
                 issue_id = issue
                selected_data = data["data"]
                revision= data.get("revision",None)
                from result_linker.utils.svn_utils import get_revision_number
                revision = get_revision_number(revision)
                #logger.debug("revision:{}".format(revision))
                selected_data_links = []
                for sel_data in selected_data:
                    selected_data_links.append(sel_data["svn_link"])
                selected_str = "||".join(str(x) for x in selected_data_links)
                option = 4
                from result_linker.utils.svn_utils import decode_option
                option_selected = decode_option(option)
                svn_username =  current_user.svn_username
                token = Share.share(issue_id, svn_username, selected_str, revision, option_selected)
                #Share.share(issue_id, token, current_user.login)
                session = get_redmine_session()
                repository_browser_id = get_repostitory_field_id(session)
                existing_repo_browser = session.query(CustomValue).filter(CustomValue.custom_field_id == repository_browser_id,
                        CustomValue.customized_id == issue_id).first()
                base_url = request.url_root
                base_url = base_url.strip("link/")
                #share_link = token
                share_link = base_url +"/share/link/v2/" + token
                long_text_format = "<p><a href=\"{}\" target=\"_blank\">Browse Results</a></p>".format(share_link)
                if not existing_repo_browser:
                    new_custom_value = CustomValue(customized_type="Issue",custom_field_id=repository_browser_id,
                    customized_id=int(issue_id),value=long_text_format)
                    session.add(new_custom_value)
                else:
                    existing_repo_browser.value = long_text_format
                session.commit()
                session.close()
        else:
            selected_data = data["data"]
            revision= data.get("revision",None)
            from result_linker.utils.svn_utils import get_revision_number
            revision = get_revision_number(revision)
            #logger.debug("revision:{}".format(revision))
            selected_data_links = []
            for sel_data in selected_data:
                selected_data_links.append(sel_data["svn_link"])
            selected_str = "||".join(str(x) for x in selected_data_links)
            option = 4
            from result_linker.utils.svn_utils import decode_option
            option_selected = decode_option(option)
            svn_username =  current_user.svn_username
            token = Share.share(issue_id, svn_username, selected_str, revision, option_selected)
            #Share.share(issue_id, token, current_user.login)
            session = get_redmine_session()
            repository_browser_id = get_repostitory_field_id(session)
            existing_repo_browser = session.query(CustomValue).filter(CustomValue.custom_field_id == repository_browser_id,
                    CustomValue.customized_id == issue_id).first()
            base_url = request.url_root
            base_url = base_url.strip("link/")
            #share_link = token
            share_link = base_url +"/share/link/v2/" + token
            long_text_format = "<p><a href=\"{}\" target=\"_blank\">Browse Results</a></p>".format(share_link)
            if not existing_repo_browser:
                new_custom_value = CustomValue(customized_type="Issue",custom_field_id=repository_browser_id,
                customized_id=int(issue_id),value=long_text_format)
                session.add(new_custom_value)
            else:
                existing_repo_browser.value = long_text_format
            session.commit()
            session.close()
    return jsonify({"success":True})


@link_blueprint.route("/redmine",methods=["GET", "POST"])
def link_to_ticket_from_redmine():
    """API to link the ticket with the repostiory data."""
    import jwt
    import datetime
    from result_linker.utils.rest_utilities import load_request_data
    if request.method == "POST":
        data = load_request_data(request)
        logger.info(data)
        issue_id = data["issue_id"]
        svn_username = data["svn_username"]
        svn_password = data["svn_password"]
        selected_data = data.get("data",None)
        revision= data.get("revision",None)
        from result_linker.utils.svn_utils import get_revision_number
        revision = get_revision_number(revision)
        #logger.debug("revision:{}".format(revision))
        secret_key = current_app.config["SECRET_KEY"]
        payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=99999),
                'iat': datetime.datetime.utcnow(),
                'svn_username': svn_username,
                'svn_password': svn_password,
                'issue': issue_id,
                'revision':revision,
                'data':selected_data
            }
        token = jwt.encode(payload,secret_key,algorithm='HS256').decode('UTF-8')
        logger.info("Linking data!!")
        Share.share(issue_id, token, svn_username)
        session = get_redmine_session()
        repository_browser_id = get_repostitory_field_id(session)
        existing_repo_browser = session.query(CustomValue).filter(CustomValue.custom_field_id == repository_browser_id,
                CustomValue.customized_id == issue_id).first()
        base_url = request.url_root
        base_url = base_url.strip("link/")
        #logger.info("request : {}".format(base_url))
        #share_link = token
        share_link = base_url +"/share/link/" + token
        long_text_format = "<p><a href=\"{}\" target=\"_blank\">Browse Results</a></p>".format(share_link)
        if not existing_repo_browser:
            new_custom_value = CustomValue(customized_type="Issue",custom_field_id=repository_browser_id,
            customized_id=int(issue_id),value=long_text_format)
            session.add(new_custom_value)
            logger.info("Updated data : {}".format(long_text_format))
        else:
            logger.info("Result data already exists!")
        session.commit()
        session.close()
    return jsonify({"success":True})