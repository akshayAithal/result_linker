#!/usr/bin/env python
# -*- coding: utf- -*-

import json


def load_request_data(request_obj):
    """Reads request sent to a client and then loads the json from it."""
    decoded_request_data = request_obj.data.decode().strip()
    if decoded_request_data != "":
        data = json.loads(request_obj.data.decode())
    else:
        data = {}
    return data

def _create_identifier(request):
    import hashlib
    base = "%s|%s" .format(request.remote_addr,request.headers.get("User-Agent"))
    hsh = hashlib.md5()
    hsh.update(base.encode("utf8"))
    import re
    digest_string = "".join( chr(x) for x in bytearray(hsh.digest()) )
    safe_digest = re.sub(r'[^\w\d-]','_',digest_string)
    return safe_digest