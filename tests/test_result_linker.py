#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `result_linker` package."""

import pytest

from click.testing import CliRunner

from result_linker import result_linker
from result_linker import cli

from result_linker.logger import logger 
from flask_login import login_required, current_user, login_user
from result_linker.models.users import User
from result_linker.models.mappings import Mapping
from result_linker.app import create_app
from result_linker.utils.svn_utils import get_folder_with_all_children 

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')



def test_login():
    test_app = create_app(config_filename="config.py")
    user = User.query.filter_by(login="akshay.aithal").first()
    login_user(user, remember=True)
    
def test_get_folder_with_all_children():
    """
    """
    test_login()
    logger.debug(get_folder_with_all_children(" svn://dllohsr222/XT4210/apps/applications/result_linker/"))
    


