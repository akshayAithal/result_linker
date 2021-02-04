# This script is a one time thing please so not use this!!
# Only for reference purpose!!!
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from result_linker.models.easyredmine.base import Base
from result_linker.models.easyredmine.custom_values import CustomValue
from result_linker.models.easyredmine.custom_fields import CustomField
from result_linker.models.easyredmine.issues import Issue

def get_repostitory_field_id(session):
    custom_field = session.query(CustomField).filter(
        CustomField.type_ == "IssueCustomField",
        CustomField.name == "Link To Results").first()
    return custom_field.id_

def populate_redmmine():
    import jwt
    session = get_redmine_session()
    issues = session.query(Issue).all()
    session.close()    
    import datetime
    for issue in issues:
        mapped_obj = Mapping.get_mapping_for(issue.id_)
        if(mapped_obj):
            session = get_redmine_session()
            logger.info("Mapped object found {}".format(issue.id_))
            secret_key = current_app.config["SECRET_KEY"]
            payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=99999),
                    'iat': datetime.datetime.utcnow(),
                    'svn_username': current_user.svn_username,
                    'svn_password': current_user.svn_password,
                    'issue': issue.id_,
                    'revision':None,
                    'data':[]
                }
            token = jwt.encode(payload,secret_key,algorithm='HS256').decode('UTF-8')
            repository_browser_id = get_repostitory_field_id(session)
            existing_repo_browser = session.query(CustomValue).filter(CustomValue.custom_field_id == repository_browser_id,
                    CustomValue.customized_id == issue.id_).first()
            base_url = request.url_root
            base_url = base_url.strip("link/")
            base_url ="http://simulation.driveline.gkn.com:4003"
            #share_link = token
            share_link = base_url +"/share/link/" + token
            long_text_format = "<p><a href=\"{}\" target=\"_blank\">Browse Results</a></p>".format(share_link)
            if not existing_repo_browser:
                new_custom_value = CustomValue(customized_type="Issue",custom_field_id=repository_browser_id,
                customized_id=int(issue.id_),value=long_text_format)
                session.add(new_custom_value)
            else:
                existing_repo_browser.value = long_text_format
            session.commit()
            session.close()
        else:
            logger.info("Mapped object not found {}".format(issue.id_))

def get_all_map_results_feilds():
    session = get_redmine_session()
    issues = session.query(Issue).all()
    session.close()
    repository_browser_id = get_repostitory_field_id(session)
    for issue in issues:
        logger.info("Checking {}".format(issue.id_))
        existing_repo_browser = session.query(CustomValue).filter(CustomValue.custom_field_id == repository_browser_id,
                    CustomValue.customized_id == issue.id_).first()
        if existing_repo_browser and "Map Results" in existing_repo_browser.value:
            session = get_redmine_session() 
            current_value = existing_repo_browser.value
            current_value = current_value.replace("Map Results","Browse Results")
            existing_repo_browser.value = current_value
            logger.info("Found and changing{}".format(issue.id_))
            session.commit()
            session.close()
