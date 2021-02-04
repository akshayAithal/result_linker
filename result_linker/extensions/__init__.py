#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""All the flask extensions are placed in this folder
so that they can be used with the application."""



from .bcrypt import bcrypt
from .login_manager import login_manager
from .scheduler import scheduler
from .migrate import migrate
from .jwt_tokens import jwt