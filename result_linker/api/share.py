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
from result_linker.utils.svn_utils import get_icons, get_folder_with_all_children_and_root, decode_option, create_public_data_for_given_template
from result_linker.models.share import Share
from result_linker.models.public import Public
share_blueprint = Blueprint("share", __name__)


@share_blueprint.route("/<issue_id>")
@login_required
def share_link(issue_id):
    """API to return the share link."""
    import jwt
    import datetime
    secret_key = current_app.config["SECRET_KEY"]
    payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'svn_username': current_user.svn_username,
            'svn_password': current_user.svn_password,
            'issue': issue_id,
        }
    token = jwt.encode(payload,secret_key,algorithm='HS256').decode('UTF-8')
    return jsonify({"token":token})
 
@share_blueprint.route("/link/",methods=["GET", "POST"])
def share_link_with_extra():
    """API to return the share link. with selected folders as well"""
    import jwt
    import datetime
    if request.method == "GET":
        return jsonify({"success":True})
    if request.method == "POST":
        from result_linker.utils.rest_utilities import load_request_data
        data = load_request_data(request)
        issue_id = data["issue_id"]
        selected_data = data["data"]
        selected_data_links = []
        from_svn_linker = data.get("svn_linker",False)
        for sel_data in selected_data:
            selected_data_links.append(sel_data["svn_link"])
        selected_str = "||".join(str(x) for x in selected_data_links)
        revision= data.get("revision",None)
        option = data["option"]
        option_selected = decode_option(option)
        if from_svn_linker:
            svn_linker_user =  data.get("user_login","")
            svn_username = "{}(From SVN Linker)".format(svn_linker_user)
            template_type = data.get("template_type","")
            create_public_data_for_given_template(issue_id,template_type,svn_username)
        else:
            svn_username =  current_user.svn_username
        svn_root_folder = data.get("root_folder",None)
        if not svn_root_folder:
            if issue_id:
                mapped_obj = Mapping.get_mapping_for(issue_id)
                svn_root_folder = mapped_obj.link
        id_ = Share.share(issue_id, svn_username, selected_str, revision, option_selected,svn_root_folder)
        #from result_linker.utils.svn_utils import get_revision_number
        #revision = get_revision_number(revision)
        #logger.debug("revision:{}".format(revision))
        #secret_key = current_app.config["SECRET_KEY"]
        #payload = {
        #        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=9999),
        #        'iat': datetime.datetime.utcnow(),
        #        'svn_username': current_user.svn_username,
        #        'svn_password': current_user.svn_password,
        #        'issue': issue_id,
        #        'revision':revision,
        #        'data':selected_data,
        #        'option_selected':option_selected
        #    }
        #token = jwt.encode(payload,secret_key,algorithm='HS256').decode('UTF-8')
        #id_ = Share.share(issue_id, token, current_user.svn_username)
        return jsonify({"token":id_})



@share_blueprint.route("/link/<token>")
def check_share_link(token):
    """API to return the root repositories given an issue ID."""
    import jwt
    import datetime
    secret_key = current_app.config["SECRET_KEY"]
    from random import randint
    #logger.info("Its Not coming here")
    try:
        payload = jwt.decode(token, secret_key)
        random_guest = randint(000000, 999999)
        login = "GUEST_{}".format(random_guest)
        from result_linker.models.user_type import UserType
        user_type = UserType.GUEST
        svn_username = payload['svn_username']
        svn_password = payload['svn_password']
        user = User(login, "guess_me",svn_password, user_type, svn_username)
        datas = payload['data']
        option_selected = payload.get('option_selected',None)
        revision = payload.get('revision',None)
        session["revision_state"] = revision
        from result_linker.utils.svn_utils import get_revision_number
        revision = get_revision_number(revision)
        #logger.debug(payload)
        allowed_list = []
        for data in datas:
            if data.get("svn_link"):
                allowed_list.append(data.get("svn_link"))
        #logger.info(allowed_list)
        user.set_svn_username_password(svn_username,svn_password)
        db.session.add(user)
        db.session.commit()
        session["option_selected"] =  option_selected
        if option_selected == "preselected_all_revision" or option_selected == "public_all_revision":
            session["allow_revisions"] = True
        else:
            session["allow_revisions"] = False
        login_user(user,  remember=False)
        logger.debug("Logging in...")
        session["allow_data"] = allowed_list
        if revision:
            #logger.debug("Inside...")
            session["revision"] = revision
        if option_selected == "preselected_new_revision":
            session["revision"] = None
            session["revision_state"] = None
        issue = payload['issue']
        if issue:
            session["issue_id"] = issue
        session["svn_username"] = svn_username
        session["svn_password"] = svn_password
        session["authorized_already"] = True
        #logger.debug(session)
        return redirect(url_for("home.index"))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home.index"))
    except jwt.InvalidTokenError:
        return redirect(url_for("home.index"))
    return redirect(url_for("home.index"))

@share_blueprint.route("/link/v2/<token>")
def check_share_link_v2(token):
    """API to return the root repositories given an issue ID."""
    import jwt
    import datetime
    #try:
    browser = request.user_agent.string
    if "ms-office" in browser or  "Microsoft Office" in browser:
        return '''<html>
            <meta http-equiv="refresh" content="time; URL={}" />
        </html>
        '''.format(request.url)
    logger.info("{} is bieng visited by {}".format(request.url,request.remote_addr))
    secret_key = current_app.config["SECRET_KEY"]
    from random import randint
    #logger.info("Its Not coming here")
    share_obj, err_msg= Share.check_valid_id(token)
    if share_obj:
        #payload = jwt.decode(jwt_token, secret_key)
        random_guest = randint(000000, 999999)
        login = "GUEST_{}".format(random_guest)
        from result_linker .models.user_type import UserType
        user_type = UserType.GUEST
        svn_username = current_app.config["GUEST_SVN_USERNAME"]
        svn_password = current_app.config["GUEST_SVN_PASSWORD"]
        user = User(login, "guess_me",svn_password, user_type, svn_password)
        datas = share_obj.shared_files
        if datas:
            selected_data = datas.split("||")
        else:
            selected_data = []
        option_selected = share_obj.option
        if share_obj.revision:
            revision = share_obj.revision
        else:
            revision = None
        session["revision_state"] = revision
        from result_linker.utils.svn_utils import get_revision_number
        revision = get_revision_number(str(revision))
        #logger.debug(payload)
        allowed_list = selected_data
        user.set_svn_username_password(svn_username,svn_password)
        db.session.add(user)
        db.session.commit()
        session["option_selected"] =  option_selected
        if option_selected == "preselected_all_revision" or option_selected == "public_all_revision":
            session["allow_revisions"] = True
        else:
            session["allow_revisions"] = False
        login_user(user,  remember=False)
        logger.debug("Logging in...")
        session["allow_data"] = allowed_list
        if revision:
            #logger.debug("Inside...")
            session["revision"] = revision
        if option_selected == "preselected_new_revision":
            session["revision"] = None
            session["revision_state"] = None
        issue = share_obj.issue
        if issue:
            session["issue_id"] = issue
        elif issue == 0 or not issue:
            session["issue_id"] = 0
        session["svn_username"] = svn_username
        session["svn_password"] = svn_password
        root_link = share_obj.root_folder
        session["root_folder"] = root_link
        session["authorized_already"] = True
        #logger.debug(session)
        return redirect(url_for("home.index"))
    else :
        return redirect(url_for("home.index"))
    #except:
    #    return redirect(url_for("home.index"))
    return redirect(url_for("home.index"))

