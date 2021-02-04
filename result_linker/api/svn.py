#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import warnings
import pathlib
import shutil

from flask import Blueprint, abort, flash
from flask import request, render_template, jsonify, current_app
from flask_login import login_required, current_user

import svnlib

from result_linker.logger import logger
from result_linker.models.mappings import Mapping
from result_linker.utils.svn_utils import (get_icons, get_root_folder,
get_all_folders_for_given_link,get_root_folder_for_projects, 
get_partent_folder, check_if_given_link_is_repo, 
check_if_project_is_small, get_folder_with_all_children_and_root)
from result_linker.utils.rest_utilities import load_request_data, _create_identifier


svn_blueprint = Blueprint("svn", __name__)


@svn_blueprint.route("/<issue_id>")
@login_required
def results(issue_id):
    """API to return the root repositories given an issue ID."""
    mapped_obj = Mapping.get_mapping_for(issue_id)
    logger.debug(current_user)
    is_small_project = check_if_project_is_small(mapped_obj.link)
    guest_user = False
    from result_linker .models.user_type import UserType
    if current_user.type_ == UserType.GUEST:
        guest_user = True
    timestamp = ""
    folder_list = get_root_folder(mapped_obj.link, issue_id)
    return jsonify(folder_list)
 


@svn_blueprint.route("/all/<issue_id>")
@login_required
def all_results(issue_id):
    """API to return the all the repositories
    Only to be used for testing!!"""
    import time
    start = time.time()
    mapped_obj = Mapping.get_mapping_for(issue_id)
    folder_list = get_folder_with_all_children_and_root(mapped_obj.link)
    end = time.time()
    logger.debug("Time taken : {}".format(end - start))
    return jsonify(folder_list)


@svn_blueprint.route("/get_folders",methods=["GET", "POST"])
@login_required
def get_folders():
    """API to return the root repositories given an issue ID."""
    if request.method == "POST":
        data = load_request_data(request)
        logger.info(data)
        svn_link= data["svn_link"]
        public_permission = data["public_permission"]
        revisions = data["revision"]
        mode = data["mode"]
        from result_linker.utils.svn_utils import get_revision_number
        revisions = get_revision_number(revisions)
        if svn_link and svn_link[-1] is not "/":
            svn_link += "/"
        folder_list = get_all_folders_for_given_link(svn_link, public_permission, revisions, mode)
        return jsonify(folder_list)
    else:
        return jsonify({"success":True})
 

@svn_blueprint.route("root")
@login_required
def get_root_results():
    """API to return the root repositories given an issue ID."""
    logger.info(current_app)
    folder_list = get_root_folder_for_projects()
    return jsonify(folder_list)



@svn_blueprint.route("/go_up",methods=["GET", "POST"])
@login_required
def go_up():
    """API go up the folder in svn."""
    if request.method == "POST":
        data = load_request_data(request)
        svn_link= data["svn_link"]
        if(check_if_given_link_is_repo(svn_link)):
            return jsonify({"message":"You have reached the root of the repository!"})
        folder_list = get_partent_folder(svn_link)
        return jsonify(folder_list)
    else:
        return jsonify({"success":True})


@svn_blueprint.route("/get_revisions",methods=["GET", "POST"])
@login_required
def get_revisions():
    """API to to return all the revisions available."""
    if request.method == "POST":
        data = load_request_data(request)
        svn_link= data.get("svn_link","")
        if len(svn_link):
            from result_linker.utils.svn_utils import  get_all_revisions_available 
            revision_list = get_all_revisions_available(svn_link)
            return jsonify(revision_list)
        else:
            return jsonify({"success":False})
    else:
        return jsonify({"success":True})



@svn_blueprint.route("/update_data",methods=["GET", "POST"])
@login_required
def update_data():
    """API to return the root repositories given an issue ID."""
    if request.method == "POST":
        files_data = request.files
        uploaded_file = files_data.get("files")
        logger.info(files_data)
        logger.info(uploaded_file)
        id_ = 0000
        username = current_user.login
        digest = _create_identifier(request)
        logger.info(digest)
        foldername = "{}_{}".format(username, digest)
        from werkzeug.utils import secure_filename
        filename = secure_filename(uploaded_file.filename)
        extension = os.path.splitext(filename)[1].lower()
        work_folder = pathlib.Path(current_app.instance_path) / foldername
        if not work_folder.exists():
            work_folder.mkdir()
        uploads_folder = work_folder / "uploads"
        if not uploads_folder.exists():
            uploads_folder.mkdir()
        destination = uploads_folder / filename
        uploaded_file.save(str(destination))
        return jsonify({"success":True,"folder_name":str(work_folder)})

@svn_blueprint.route("/commit_data",methods=["GET", "POST"])
@login_required
def commit_data():
    if request.method == "POST":
        data = load_request_data(request)
        svn_link= data["svn_link"]
        message= data["commit_message"]
        svn_username= current_user.svn_username
        svn_password= current_user.svn_password
        digest = _create_identifier(request)
        #try:
        foldername = "{}_{}".format(svn_username, digest)
        uploads_folder = os.path.join(current_app.instance_path,foldername ,"uploads")
        if not os.path.exists(uploads_folder):
            os.mkdir(uploads_folder)
        logger.info(uploads_folder)
        checkout_folder = os.path.join(current_app.instance_path,foldername ,"checkout")
        if not os.path.exists(checkout_folder):
            os.mkdir(checkout_folder)
        files = os.listdir(uploads_folder)
        if os.path.exists(uploads_folder) and len(files):
            logger.info("Data uploaded!!")
        svn_file_list, _ = svnlib.list_folder(svn_link, svn_username, svn_password)
        checkout_type ="empty"
        logger.info(files)
        logger.info(svn_file_list)
        for i in files:
            if i in svn_file_list:
                checkout_type ="immediates"
                break
        logger.info(checkout_type)
        checked_out_path = svnlib.checkout(svn_link, checkout_folder, svn_username, 
        svn_password, depth=checkout_type)
        dir_list = os.listdir(checked_out_path)
        if ".svn" not in dir_list: 
            for i in dir_list:
                new_checked_out_path = os.path.join(checked_out_path,i)
                dir_list = os.listdir(new_checked_out_path)
                if ".svn" in dir_list:
                    checked_out_path = new_checked_out_path
                    break
        directory_name = ""
        for file in files:
            overwrite = False
            dir_list = os.listdir(checked_out_path)
            if ".svn" in dir_list:
                dir_list.remove(".svn")
            logger.info(dir_list)
            if checkout_type == "empty":
                directory_name = ""
            else:
                if len(dir_list) >= 1:
                    directory_name = dir_list[0]
                else:
                    directory_name = ""
            if(len(dir_list) == 0 ):
                destination = os.path.join(checked_out_path,directory_name, file)
            else:
                destination = os.path.join(checked_out_path, file)
            if  os.path.exists(destination):
                overwrite = True
                import subprocess
            shutil.move(os.path.join(uploads_folder, file), destination)
            if not overwrite:
                import subprocess
                args = ["svn", "add", destination]
                process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            else:
                args = ["svn", "resolve", file, "--accept","mine-full"]
                process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        commit_message = "Commit from result linker"
        if "." in directory_name:
            commit_path = checked_out_path
        else:
            commit_path = os.path.join(checked_out_path,directory_name)
        svnlib.commit(commit_path, svn_username, svn_password, "." , message)
        #Delete the folder once done
        del_folder = os.path.join(current_app.instance_path,foldername)
        shutil.rmtree(del_folder)
        return jsonify({"success":True})
        #except:
        #    pass
        return jsonify({"success":False})
    

@svn_blueprint.route("/for_link",methods=["GET", "POST"])
@login_required
def results_for_link():
    """API to return the root repositories given an svn link."""
    if request.method == "POST":
        data = load_request_data(request)
        svn_link= data["svn_link"]
        #from result_linker .models.user_type import UserType
        #if current_user.type_ == UserType.GUEST:
        #    guest_user = True
        #timestamp = ""
        issue_id = ""
        folder_list = get_root_folder(svn_link, issue_id)
        from result_linker.models.mappings import Mapping
        mapped_objs = Mapping.get_mapped_issue(svn_link)
        ids = ','.join(str(mapped_obj.issue) for mapped_obj in mapped_objs)
        return jsonify({"data":folder_list,"ids":ids})
    return jsonify({"success":True})