#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Blueprints for the application.


"""

from result_linker.api.home import home_blueprint
from result_linker.api.user import user_blueprint
from result_linker.api.svn import svn_blueprint
from result_linker.api.download import download_blueprint
from result_linker.api.share import share_blueprint
from result_linker.api.link import link_blueprint
from result_linker.api.write import write_blueprint