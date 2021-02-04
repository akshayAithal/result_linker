#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for product_viewer."""
from result_linker.logger import logger
from result_linker.app import create_app


if __name__ == "__main__":
    logger.warning(
        "Run this using a WSGI server. "
        "Running via Flask's "
        "run command is not recommended.")
    app = create_app(config_filename="config.py")
    app.run(
        host="0.0.0.0",
        port="2323",
        threaded=True)
