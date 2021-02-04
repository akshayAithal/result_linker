#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import warnings

from flask import Blueprint, jsonify, request, send_file, session
from flask import request, render_template, jsonify, abort
from flask_login import login_required, current_user

import svnlib

from result_linker.logger import logger
from result_linker.models.mappings import Mapping
from result_linker.utils.svn_utils import get_icons, get_folder_with_all_children,process_data_to_download, process_file_to_download
from result_linker.utils.rest_utilities import load_request_data
from result_linker.models.process import Process, clear_out_old_process

download_blueprint = Blueprint("download", __name__)

def set_download_progress(key,progress):
    """
    To set the download progress
    """
    Process.set_process_progress(key,progress)

def process_timestamp(timestamp):
    new_timstamp = timestamp.replace("/","_").replace(":","_").replace(" ","").replace(",","")
    return new_timstamp

@download_blueprint.route("/",methods=["GET", "POST"])
@login_required
def download():
    """For the links posted zip and download!!"""
    if request.method == "POST":
        data = load_request_data(request)
        svn_link_objects = data["data"]
        timestamp = data["time_stamp"]
        timestamp = process_timestamp(timestamp)
        issue_id = data["issue_id"]
        revision = data.get("revision","")
        from result_linker.utils.svn_utils import get_revision_number
        revision = get_revision_number(revision)
        set_download_progress(timestamp,0)
        #logger.debug(svn_link_objects)
        from flask import current_app
        instance_path = current_app.instance_path
        set_download_progress(timestamp,10)
        zip_file_name = process_data_to_download(svn_link_objects,timestamp,instance_path, issue_id, revision)
        set_download_progress(timestamp,90)
        if Process.check_for_cancel(timestamp):
            return abort(401)
        response = send_file(zip_file_name,attachment_filename="downloaded_data.zip",as_attachment=True)
        #logger.info("Session value set")
        set_download_progress(timestamp,100)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(clear_out_old_process())
        loop.close()
        return response
        #return jsonify({"success": True})
    if request.method == "GET":
        logger.debug("here in GET!!")
        return jsonify({"success": True})

@download_blueprint.route("/progress/<key>",methods=["GET"])
@login_required
def progress(key):
    """For the links posted zip and download!!"""
    if request.method == "GET":
        progress = Process.get_process_progress(key)
        if not progress:
            progress = 0
        return jsonify({"success": True,"progress":progress})

@download_blueprint.route("/cancel/<key>",methods=["GET"])
@login_required
def cancel(key):
    """For the links posted zip and download!!"""
    if request.method == "GET":
        Process.cancel_process(key)
        return jsonify({"success": True})

@download_blueprint.route("/open/",methods=["GET","POST"])
@login_required
def open():
    """For the links posted zip and download!!"""
    if request.method == "GET":
        return jsonify({"success": True})
    elif request.method == "POST":
        data = load_request_data(request)
        svn_link_objects = data["data"]
        timestamp = data["time_stamp"]
        timestamp = process_timestamp(timestamp)
        issue_id = data["issue_id"]
        revision = data.get("revision","")
        from result_linker.utils.svn_utils import get_revision_number
        revision = get_revision_number(revision)
        set_download_progress(timestamp,0)
        #logger.debug(svn_link_objects)
        from flask import current_app
        instance_path = current_app.instance_path
        set_download_progress(timestamp,10)
        folder_path = os.path.join(os.path.normpath(current_app.static_folder),"exported_files")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        exported_file_path = process_file_to_download(svn_link_objects,timestamp,folder_path, issue_id, revision)
        import platform
        if platform.system() == "Windows":
            assets_file_path = exported_file_path.split("\\ui")
        else:
            assets_file_path = exported_file_path.split("/ui")
        return jsonify({"exported_file_path": assets_file_path[1]})

