#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, jsonify, request, abort, session, current_app
from flask_login import login_user, login_required, logout_user,current_user
from flask_jwt_extended import (create_access_token, create_refresh_token)

import svnlib
from redminelib import Redmine


from result_linker.logger import logger
from result_linker.models.users import User
from result_linker.models import db
from result_linker.utils.rest_utilities import load_request_data, _create_identifier


user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Route allowing login
    Use with POST
    Send a json with username and password in the keys.
    Optionally use remember_me if you want to set cookies."""
    if request.method == "GET":
        return jsonify(
            {"success": False,
            "message": "Need to login first!"})
    else:
        login = request.get_json()["username"]
        password = request.get_json()["password"]
        logger.debug("Attempting to login as {}".format(login))
        user = User.query.filter_by(login=login).first()
        issue_id = session.get("issue_id",0)
        logger.info(" Issue id {}".format(issue_id))
        session["allow_revisions"] = True
        address = current_app.config["REDMINE_ADDRESS"]
        try:
            redmine_user = Redmine(address, username=login, password=password).auth()
        except Exception as err:
            redmine_user = None
        if redmine_user and user:
            custom_field_list = redmine_user.custom_fields["_resources"]
            svn_password = ""
            for custom_field in custom_field_list:
                if custom_field["id"] == 102:
                    svn_password = custom_field["value"]
                    break
            if user.check_password(password) and svn_password == user.svn_password:
                remember_me = request.get_json()["remember_me"]
                login_user(user, remember=remember_me)
                logger.info(f"{user.login} was logged in and will {'be' if remember_me else 'not be'} remembered.")
                if(issue_id):
                    session["issue_id"] = issue_id
                return jsonify({"success": True})
            else:
                user.change_password(password,svn_password)
                db.session.commit()
                login_user(user, remember=remember_me)
                logger.info(f"{user.login} was logged in and will {'be' if remember_me else 'not be'} remembered.")
                if(issue_id):
                    session["issue_id"] = issue_id
                return jsonify({"success": True})
        else:
            if redmine_user:
                custom_field_list = redmine_user.custom_fields["_resources"]
                svn_password = ""
                for custom_field in custom_field_list:
                    if custom_field["id"] == 102:
                        svn_password = custom_field["value"]
                        break
                from result_linker .models.user_type import UserType
                user_type = UserType.USER
                user = User(login, password,svn_password, user_type)
                db.session.add(user)
                db.session.commit()
                remember_me = request.get_json()["remember_me"]
                login_user(user, remember=remember_me)
                #Delete the folder once done
                digest = _create_identifier(request)
                #try:
                foldername = "{}_{}".format(svn_username, digest)
                del_folder = os.path.join(current_app.instance_path,foldername)
                if os.path.exists(del_folder):
                    shutil.rmtree(del_folder)
                logger.info(f"{user.login} was logged in and will {'be' if remember_me else 'not be'} remembered.")
                if(issue_id):
                    session["issue_id"] = issue_id
                return jsonify({"success": True})
            else:
                logger.warning("{} is not an accepted user! or Wrong password".format(login))
                return abort(401)

@user_blueprint.route("/check_login")
@login_required
def check_login():
    """Checks if a user is logged in"""
    guest_user = False
    from result_linker .models.user_type import UserType
    if current_user.type_ == UserType.GUEST:
        guest_user = True
    issue_id = ""
    issue_id = session.get("issue_id")
    revision_state = session.get("revision_state")
    allow_revisions = session.get("allow_revisions")
    root_folder = session.get("root_folder")
    return jsonify({"success": True,
    "username":current_user.login,
    "guest":guest_user,
    "issue_id":issue_id,
    "revision":revision_state,
    "allow_revisions":allow_revisions,
    "root_folder":root_folder
    })


@user_blueprint.route("/logout")
@login_required
def logout():
    curent_login = current_user.login
    delete_flag  = False
    from result_linker .models.user_type import UserType
    if current_user.type_ == UserType.GUEST:
        if current_user.login is not "temp":        
            delete_flag = True
    logout_user()
    #if "issue_id" in session:
    #    session["issue_id"] =  None
    if "svn_username" in session:
        session["svn_username"] =  None
    if "svn_password" in session:
        session["svn_password"] =  None
    if "authorized_already" in session:
        session["authorized_already"] =  None
    if "allow_data" in session:
        session["allow_data"] =  None
    if "revision_state" in session:
        session["revision_state"] =  None
    if "revision" in session:
        session["revision"] =  None
    if "allow_revisions" in session:
        session["allow_revisions"] =  None
    if delete_flag:
        user_to_be_deleted = User.query.filter_by(login=curent_login).first()
        logger.info("User {} deleted".format(login))
        db.session.delete(user_to_be_deleted)
        db.session.commit()   
    return jsonify({"success": True})


@user_blueprint.route("/onetime")
def run_api():
    #logger.info("Here we go!!")
    from result_linker.utils.populate_redmine import populate_redmmine, get_all_map_results_feilds
    if request.method == "GET":
        #get_all_map_results_feilds()
        pass
    return jsonify({"success": True})
