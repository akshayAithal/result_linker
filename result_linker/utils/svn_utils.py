#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import warnings
import asyncio

import svnlib
from flask import current_app, session
from flask_login import login_required, current_user
from result_linker.logger import logger
from result_linker.models.mappings import Mapping
from result_linker.models.process import Process

def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)


def set_download_progress(key,progress):
    """
    To set the download progress
    """
    if not key or not len(key):
        return
    Process.set_process_progress(key,progress)

def cleanup_old_files(path):
    """
    Delete the old file before a day
    """
    logger.info(path)
    import time
    current_time = time.time()
    for file in os.listdir(path):
        if file.endswith(".zip"):
            creation_time = os.path.getctime(os.path.join(path,file))
            if (current_time - creation_time) // (24 * 3600) >= 1:
                os.remove(os.path.join(path,file))
                logger.info("Removing old file {}".format(file))
    

def get_icons(extension):
    icons = {
        ".xlsx": "xls.png",
        ".xls": "xls.png",
        ".csv": "xls.png",
        ".pptx": "ppt.png",
        ".ppt": "ppt.png",
        ".php": "php.png",
        ".png": "picture.png",
        ".psd": "psd.png",
        ".jpeg": "picture.png",
        ".jpg": "picture.png",
        ".gif": "picture.png",
        ".bmp": "picture.png",
        ".tiff": "picture.png",
        ".pdf": "pdf.png",
        ".css": "css.png",
        ".bin": "application.png",
        ".exe": "application.png",
        ".out": "application.png",
        ".mov": "film.png",
        ".mpeg": "film.png",
        ".mpg": "film.png",
        ".wmv": "film.png",
        ".mp4": "film.png",
        ".avi": "film.png",
        ".divx": "film.png",
        ".zip": "zip.png",
        ".gz": "zip.png",
        ".tar.gz": "zip.png",
        ".tar": "zip.png",
        ".7zip": "zip.png",
        ".rar": "zip.png",
        ".rb": "ruby.png",
        ".html": "html.png",
        ".htm": "html.png",
        ".xhtm": "html.png",
        ".xml": "html.png",
        ".mp3": "music.png",
        ".wav": "music.png",
        ".flac": "music.png",
        ".sh": "script.png",
        ".ini": "script.png",
        ".yaml": "script.png",
        ".yml": "script.png",
        ".toml": "script.png",
        ".cfg": "script.png",
        ".in": "script.png",
        ".json": "script.png",
        ".db": "db.png",
        ".db": "db.png",
        ".psd": "psd.png",
        ".docx": "doc.png",
        ".doc": "doc.png",
        ".py": "code.png",
        ".txt": "txt.png",
        ".md": "txt.png",
        ".rst": "txt.png"
    }
    icon = icons.get(extension, "file.png")
    return icon

async def get_folder_with_all_children(link, public_permission = False, time_stamp= None):
    logger.debug("Getting data for {}".format(link))
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    folders, _ = svnlib.list_folder(
    link , svn_username, svn_password)
    parent_url = link
    folder_list = []
    include_parent = False
    files_public = False
    allowed_list = session.get("allow_data",[])
    permitted_folders, permitted_files, public_files, public_folders = get_all_permitted_links_in_the_folder(link, folders)
    permitted_list = []
    permitted_list.extend(permitted_folders)
    permitted_list.extend(permitted_files)
    permitted_list = list(set(permitted_list))
    coros = [process_folder(folder, parent_url , public_permission, files_public, allowed_list, time_stamp) for folder in folders]  
    results = await asyncio.gather(*coros)
    for result in results:
        if result[1]:
            include_parent = True
        if result[0]:
            folder_list.append(result[0])
    return folder_list, include_parent

def get_all_permitted_links_in_the_folder(link, folders):
    """ To get all aloowed and permitted links
    """
    allowed_list = session.get("allow_data",[])
    issue_id = session.get("issue_id",None) 
    # Get data from the public data in SVN
    public_files =  session.get("public_files",[])
    public_folders =  session.get("public_folders",[])
    permitted_files = []
    permitted_folders = []
    public_files_full = []
    public_folders_full = []
    parent_url = link
    if len(public_files):
        for file in  public_files:
            file = file.replace(link,"")
            file = file.replace("./","")
            if file.startswith("/"):
                file = file[1:]
            dirs = file.split("/")
            final_url = ""
            if len(dirs) and (dirs[0] in folders or dirs[0]+ "/" in folders):
                if len(dirs) == 1:
                    final_url = link + dirs[0]
                else:
                    final_url = link + dirs[0] +"/"
            if len(final_url):
                permitted_files.append(final_url)
    if len(public_folders):
        for file in  public_folders:
            if file == link:
                permitted_folders.append(file)
            file = file.replace(link,"")
            file = file.replace("./","")
            if file.startswith("/"):
                file = file[1:]
            dirs = file.split("/")
            filtered_dirs = [x for x in dirs if x]
            final_url = ""
            for i , _dir in enumerate(filtered_dirs):
                if (filtered_dirs[i] in folders or filtered_dirs[i]+ "/" in folders):
                    if i == (len(filtered_dirs) -1):
                        final_url = link + filtered_dirs[i] +"/"
                    else:
                       final_url = link + filtered_dirs[i] +"/"
                if len(final_url):
                    break
            if len(final_url):
                permitted_folders.append(final_url)
    if allowed_list and len(allowed_list):
        for allowed_value in  allowed_list:
            file = allowed_value.replace(link,"")
            #Folder
            if file.endswith("/"):
                dirs = file.split("/")
                filtered_dirs = [x for x in dirs if x]
                final_url = ""
                for i , _dir in enumerate(filtered_dirs):
                    if (filtered_dirs[i] in folders or filtered_dirs[i]+ "/" in folders):
                        if i == (len(filtered_dirs) -1):
                            final_url = link + filtered_dirs[i] +"/"
                        else:
                            final_url = link + filtered_dirs[i] +"/"
                    if len(final_url):
                        break
                if len(final_url):
                    permitted_folders.append(final_url)
            else:
                dirs = file.split("/")
                final_url = ""
                if len(dirs) and (dirs[0] in folders or dirs[0]+ "/" in folders):
                    if len(dirs) == 1:
                        final_url = link + dirs[0]
                    else:
                        final_url = link + dirs[0] +"/"
                if len(final_url):
                    permitted_files.append(final_url)
    permitted_folders = list(set(permitted_folders))
    permitted_files = list(set(permitted_files))
    # Code to get full links for public folders
    if issue_id:
        mapped_obj = Mapping.get_mapping_for(issue_id)
        svn_link = mapped_obj.link
    else:
        svn_link = link
    for public_fodler in public_folders:
        pub_full_name = ""
        if  "./" in public_fodler:
            if svn_link[-1] is not "/":
                svn_link = svn_link + "/"
            pub_full_name = public_fodler.replace("./",svn_link)
        else:
            pub_full_name = public_fodler
        if pub_full_name:
            public_folders_full.append(pub_full_name)
    for public_file in public_files:
        pub_full_name = ""
        if  "./" in public_file:
            if svn_link[-1] is not "/":
                svn_link = svn_link + "/"
            pub_full_name = public_file.replace("./",svn_link)
        else:
            pub_full_name = public_file
        if pub_full_name:
            public_files_full.append(pub_full_name)
    #permitted_allowed_list = list(set(permitted_allowed_list))
    return permitted_folders, permitted_files, public_files_full, public_folders_full


def get_all_folders_for_given_link(link, public_permission = False, revision = "", mode= ""):
    logger.debug("Getting data for {}".format(link))
    #logger.debug(public_permission)
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    if not len(revision.strip()):
        revision = session.get("revision","")
    if revision and len(revision.strip()):
        folders, _ = svnlib.list_folder(
        link , svn_username, svn_password,revision=revision)
    else:
        folders, _ = svnlib.list_folder(
        link , svn_username, svn_password)
    #logger.debug("Got data {}".format(folders))
    parent_url = link
    folder_list = []
    files_public = False
    allowed_list = session.get("allow_data",[])
    permitted_folders, permitted_files, public_files, public_folders = get_all_permitted_links_in_the_folder(link, folders)
    permitted_list = []
    permitted_list.extend(permitted_folders)
    permitted_list.extend(permitted_files)
    if parent_url in permitted_folders:
        public_permission = True
    if allowed_list and len(allowed_list):
        permitted_list.extend(allowed_list)
    permitted_list = list(set(permitted_list))
    for folder in folders:
        if folder.strip() != "":
            #logger.debug("Continuing for file {}".format(folder))
            new_permission = False
            if parent_url.endswith("/"):
                node_id = f"{parent_url[:-1]}/{folder}"
            else:
                node_id = f"{parent_url}/{folder}"
            extension = os.path.splitext(folder)[1].lower()
            icon = ""
            if extension != "":
                icon = get_icons(extension)
            else:
                icon = "directory.png"
            if allowed_list and (node_id in allowed_list):
                new_permission = True
            #if current_user.type_ is UserType.GUEST
            from result_linker.models.user_type import UserType
            #logger.debug("Continuing for node {}".format(node_id))
            if node_id.endswith("/"): 
                if not public_permission and  node_id not in permitted_list:
                    continue
                map_status = False
                if node_id in public_files or node_id in public_folders or (allowed_list and node_id in allowed_list):
                    map_status = True
                mapped_objs = []
                if mode == "repo_browser" or mode == "repo_explorer":
                    mapped_objs = Mapping.get_mapped_issue(node_id)
                if mapped_objs:
                    icon = "directory_green.png"
                elif icon == "directory.png" and map_status:
                    icon = "directory_blue.png"
                folder_dict = {
                    "id": node_id,
                    "parent": parent_url,
                    "text": folder[:-1] if folder.endswith("/") else folder,
                    "children_status": True,
                    "icon" : icon,
                    "public_permission": current_user.type_ is not  UserType.GUEST or node_id in public_folders or  public_permission,
                    "children":[],
                    "map_staus": map_status,
                    "size": ""
                    }
                folder_list.append(folder_dict)
            else:
                if  not public_permission and  node_id not in permitted_list:
                    #logger.debug("Continuing for file {}".format(folder))
                    continue
                size = get_svn_file_size_for_file(node_id, svn_username, svn_password)
                logger.info("Getting info about {} ".format(node_id))
                map_status = False
                if node_id in public_files or node_id in public_folders or (allowed_list and node_id in allowed_list):
                    map_status = True
                folder_dict = {
                    "id": node_id,
                    "parent": parent_url,
                    "text": folder[:-1] if folder.endswith("/") else folder,
                    "children_status": False,
                    "icon" : icon,
                    "public_permission": True,
                    "children":[],
                    "map_staus": map_status,
                    "size":size
                    }
                folder_list.append(folder_dict)
    return folder_list

async def get_folder_with_all_children_recursively(link, public_permission = False, time_stamp = None):
    set_download_progress(time_stamp,35)
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    folders, _ = svnlib.list_folder(
    link , svn_username, svn_password)
    parent_url = link
    folder_list = []
    include_parent = False
    files_public = False
    allowed_list = session.get("allow_data",[])
    permitted_folders, permitted_files, public_files, public_folders = get_all_permitted_links_in_the_folder(link, folders)
    permitted_list = []
    permitted_list.extend(permitted_folders)
    permitted_list.extend(permitted_files)
    permitted_list = list(set(permitted_list))
    coros = [process_folder(folder, parent_url , public_permission, folder in permitted_folders, allowed_list, time_stamp) for folder in folders]  
    results = await asyncio.gather(*coros)
    for result in results:
        if result[1]:
            include_parent = True
        if result[0]:
            folder_list.append(result[0])
    if Process.check_for_cancel(time_stamp):
          return [], False
    return folder_list, include_parent

async def process_folder(folder, parent_url , public_permission, files_public, allowed_list, time_stamp):
    return_obj = None
    include_parent = False
    set_download_progress(time_stamp,40)
    if Process.check_for_cancel(time_stamp):
          return None, False
    if folder.strip() != "":
        new_permission = False
        if parent_url.endswith("/"):
            node_id = f"{parent_url[:-1]}/{folder}"
        else:
            node_id = f"{parent_url}/{folder}"
        extension = os.path.splitext(folder)[1].lower()
        icon = ""
        if extension != "":
            icon = get_icons(extension)
        else:
            icon = "directory.png"
        children, new_permission = await get_folder_with_all_children(node_id, (public_permission and not files_public), time_stamp) if folder.endswith("/") else ([],public_permission)
        children_status = True if len(children) else False
        map_status = False;
        folder_dict = {
            "id": node_id,
            "parent": parent_url,
            "text": folder[:-1] if folder.endswith("/") else folder,
            "children": children,
            "icon" : icon,
            "children_status":children_status,
            "public_permission":public_permission,
            "map_staus": map_status,
            "size":"",
        }
        if node_id in  allowed_list:
            new_permission = True
        if public_permission or new_permission:
            return_obj = folder_dict
        if new_permission:
            include_parent = True
    return  return_obj, include_parent
    
def get_folder_with_all_children_and_root(link, time_stamp=""):
    folder_list = []
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    children, _  = loop.run_until_complete(get_folder_with_all_children_recursively(link, False, time_stamp))
    folder_list.append({
    "id": link,
    "parent": "#",
    "text": link,
    "children": children,
    "icon" : "directory.png",
    "children_status":True if len(children) else False,
    "public_permission":False,
    "map_staus": False,
    "size":""
    })
    loop.close()
    return folder_list
    
def check_and_get_public_data(issue_id, link):
    from result_linker.models.public import Public
    values_set = False
    if not issue_id:
        return values_set
    public_data = Public.get_public_data_for_issue(issue_id)
    if public_data:
        public_files_list = []
        public_folders_list = []
        public_files_str = public_data.public_files
        public_folders_str = public_data.public_folder
        if public_files_str:
            public_files_list = public_files_str.split("||")
        if public_folders_str:
            public_folders_list = public_folders_str.split("||")
        session["public_files"] =  public_files_list
        session["public_folders"] =  public_folders_list
        session["root_link"] = link
        values_set = True
    return values_set


def populate_available_links(link, issue_id=""):
    """ export the public data if it exists and add them to the 
    allowed_list"""
    logger.debug("Checking for public data!!")
    if session.get("option_selected",None) and "preselected" in session["option_selected"]: 
        session["public_files"] = []
        session["public_folders"] = []
        return
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    folders, _ = svnlib.list_folder(link , svn_username, svn_password)
    if link[-1] is not "/":
        link = link + "/"
    public_data_link = "{}public_data.json".format(link)
    public_data_exists = False
    for child in folders:
        if "public_data.json" in folders:
            public_data_exists= True
            break
    is_pub_data_in_database = check_and_get_public_data(issue_id,link)
    if public_data_exists and (not is_pub_data_in_database):
        svn_username = current_user.svn_username
        svn_password = current_user.svn_password
        username = current_user.login
        instance_path = current_app.instance_path
        import datetime
        timestamp = datetime.datetime.utcnow()
        timestamp = str(timestamp).replace("/","_").replace(":","_").replace(" ","_").replace(",","").replace(".","").replace("-","_")
        data_folder = os.path.join(instance_path, "{}_{}".format(username, timestamp))
        os.mkdir(data_folder)
        res = svnlib.export(public_data_link, data_folder,svn_username,svn_password)
        logger.debug(public_data_link)
        logger.debug(res)
        import json
        file_path = os.path.join(instance_path, "{}_{}".format(username, timestamp),"public_data.json")
        logger.debug("Data exists!!!! ")
        with open(file_path) as json_file:
            data = json.load(json_file)
            public_files =  data.get("public_files", [])
            public_folders =  data.get("public_folders",[])
            session["public_files"] = public_files
            session["public_folders"] = public_folders
            session["root_link"] = link
            json_file.close()
        import shutil
        shutil.rmtree(data_folder)
    elif (not is_pub_data_in_database):
        session["public_files"] = []
        session["public_folders"] = []


def get_root_folder(link, issue_id):
    """ Coat the link from the svn linker into json data that 
        UI understands
        Shows only the root data
    """
    populate_available_links(link, issue_id)
    folder_list = []
    from result_linker.models.user_type import UserType
    revision = ""
    if session.get("revision",None):
        revision = session["revision"]
    folder_list.append({
    "id": link,
    "parent": "#",
    "text": link,
    "children": [],
    "icon" : "directory.png",
    "children_status":True,
    "public_permission": current_user.type_ is not UserType.GUEST,
    "map_status" : False,
    "size":"",
    "revision":revision
    })
    return folder_list


def zip_given_folder(src):
    """ Zip the given file
    """
    import zipfile
    zf = zipfile.ZipFile("%s.zip" % (src), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print("zipping {} as {}".format(os.path.join(dirname, filename),arcname))
            zf.write(absname, arcname)
    zf.close()


def get_the_required_files(links, path, timestamp, issue_id, revision):
    """
    Export hte give file to the directory and  zip to enable easy download
    as wll as check if they have public !!
    """
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    instance_path = path
    cleanup_old_files(path)
    import datetime,shutil
    time_stamp = timestamp
    data_folder = os.path.join(instance_path, "download_data_{}".format(time_stamp))
    os.mkdir(data_folder)
    peremissible_data = None
    #mapped_obj = Mapping.get_mapping_for(issue_id)
    #root_link = mapped_obj.link
    #logger.debug("Here in get_the_required_files")
    set_download_progress(timestamp,30)
    for data in links:
        #logger.debug("In for loop")
        #logger.debug(data)
        link = data[0]
        permission = data[1]
        current_folder = data_folder
        consider_flag  = False
        if os.path.splitext(link)[1]:
            consider_flag = True
        else:
            #if not peremissible_data:
            #    peremissible_data = get_folder_with_all_children_and_root(root_link,time_stamp)
            set_download_progress(timestamp,50)
            download_all_the_permittable(data_folder, link, revision, time_stamp, permission)
        if consider_flag:
            logger.debug("Export!! {}".format(revision))
            if(revision  and len(revision)):
                downloaded_data = svnlib.export(link, data_folder,svn_username,svn_password, revision=revision)
            else:
                downloaded_data = svnlib.export(link, data_folder,svn_username,svn_password)
    zip_given_folder(data_folder)
    if os.path.exists(data_folder):
        shutil.rmtree(data_folder)
    zip_file_name = "{}.zip".format(data_folder)
    if Process.check_for_cancel(time_stamp):
            return ""
    return zip_file_name

def download_all_the_permittable(current_dir,link, revision, timestamp, permission):
    #logger.debug("Here in download_all_the_permittable")
    if Process.check_for_cancel(timestamp):
        return
    set_download_progress(timestamp,60)
    download_the_selected_files(link,current_dir, revision, timestamp, permission)

def check_if_folder_is_permissable(peremissible_data, link):
    found_dict = None
    for data in peremissible_data:
        if data.get("id") == link:
            found_dict = data
        else :
            if data.get("children"):
                found_dict = check_if_folder_is_permissable(data.get("children"),link)
        if found_dict:
            break
    return found_dict 

def export_to_given_directory(found_dict, folder_path, revision, timestamp):
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    current_link = found_dict.get("id")
    logger.debug("Exporting {}".format(current_link))
    #logger.debug("Dict {}".format(found_dict))
    set_download_progress(timestamp,70)
    if Process.check_for_cancel(timestamp):
            return
    if revision and len(revision):
        svnlib.export(current_link, folder_path,svn_username,svn_password,depth="empty", revision= revision)
    else:
        svnlib.export(current_link, folder_path,svn_username,svn_password,depth="empty")
    children =  found_dict.get("children")
    folder_name = found_dict.get("text")
    if found_dict.get("parent") == "#":
        folder_name = folder_name.split("/")[-2]
    new_path = os.path.join(folder_path,folder_name)
    for child in children:
        if Process.check_for_cancel(timestamp):
            break
        export_to_given_directory(child, new_path, revision,timestamp)


def process_file_to_download(svn_link_objects,timestamp,instance_path, issue_id, revision=""):
    logger.debug("Processing files to download")
    link = svn_link_objects[0].get("id")
    set_download_progress(timestamp,25)
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    import datetime,shutil
    time_stamp = timestamp
    addresses = link.split("/")
    exact_file_name = addresses[-1]
    filename_changed =  False
    if exact_file_name[0] == "#":
        exact_file_name = exact_file_name[1:]
        filename_changed = True
    data_folder = os.path.join(instance_path, "open_data_{}".format(time_stamp))
    os.mkdir(data_folder)
    final_path = os.path.join(data_folder,exact_file_name)
    #if filename_changed:
    #    downloaded_data = svnlib.export(link, final_path,svn_username,svn_password)
    #else:
    downloaded_data = svnlib.export(link, data_folder,svn_username,svn_password)
    if filename_changed:
        os.rename(downloaded_data, final_path)
    #final_path = os.path.join(data_folder, exact_file_name)
    return final_path

def process_data_to_download(svn_link_objects,timestamp,instance_path, issue_id, revision=""):
    """
    """
    selected_links = []
    final_links = []
    logger.debug("Processing datat to download")
    set_download_progress(timestamp,25)
    permission_link_map = {}
    for obj  in svn_link_objects:
        link = obj.get("svn_link")
        selected_links.append(link)
        permission_link_map[link] = obj.get("permission")
    for obj  in svn_link_objects:
        parent = obj.get("parent")
        if parent not in selected_links:
            final_links.append((obj.get("svn_link"),obj.get("permission")))
    zip_file_name = ""
    if final_links:
        zip_file_name = get_the_required_files(final_links,instance_path,timestamp, issue_id, revision)
    set_download_progress(timestamp,95)
    return zip_file_name


def construct_uri(ip, port, db_type, db, username, password):
    """Returns an uri for SQLAlchemy using the given parameters."""
    try:
        from urllib import quote_plus
    except ImportError:
        from urllib.parse import quote_plus

    db_type = db_type.lower()
    if db_type == "mysql":
        dialect_driver = "mysql+pymysql"
    elif db_type == "postgresql":
        dialect_driver = "postgres+psycopg2"
    else:
        raise NotImplementedError(("Unable to process {} "
                                   "databases for now.").format(db_type))
    
    uri = "{}://{}:{}@{}:{}/{}".format(dialect_driver, username,
                                       quote_plus(password), ip,
                                       port, db)
    return uri
    
def get_redmine_session():
    from result_linker.models.easyredmine.base import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    uri = construct_uri(current_app.config["SERVER_IP"], current_app.config["PORT"],  current_app.config["DB_TYPE"],
                        current_app.config["DB_NAME"], current_app.config["USERNAME"],current_app.config["PASSWORD"] )
    engine = create_engine(uri)
    logger.debug("Created engine")
    Base.metadata.create_all(engine, checkfirst=True)
    logger.debug("Mapped base metadata.")
    Session = sessionmaker(bind=engine)
    logger.debug("Created Session class bound to engine.")
    session = Session()
    logger.debug("Created session Object")
    return session

def get_repo_data():
    from result_linker.models.easyredmine.repositories import Repository
    session = get_redmine_session()
    repo_list_qeury = session.query(Repository)
    repo_list = []
    for repo in repo_list_qeury:
        url = repo.url
        url = url.strip("\n").strip('"')
        url = url.replace("10.133.0.222","dllohsr222")
        url = url.replace("dllohsr222.driveline.gkn.com","dllohsr222")
        if url.count('/') > 3:
            continue
        repo_list.append(url)
    session.close()
    return repo_list

def get_root_folder_for_projects():
    folder_list = []
    repo_list = get_repo_data()
    repo_list = list(set(repo_list))
    repo_list = sorted(repo_list, key=str.lower)
    folder_list = []
    from result_linker.models.user_type import UserType
    for repo in repo_list:
        folder_list.append({
            "id": repo,
            "parent": "#",
            "text": repo,
            "children": [],
            "icon" : "directory.png",
            "children_status":True,
            "public_permission":  current_user.type_ is not  UserType.GUEST,
            "map_status": False
        })
    return folder_list

def check_if_given_link_is_repo(svn_link):
    if(os.path.splitext(svn_link)[1] == ""):
        svn_link = svn_link[:-1]
    repo_list = get_repo_data()
    repo_list = list(set(repo_list))
    if(svn_link in repo_list):
        return True
    else:
        return False


def get_partent_folder(svn_link):
    "get one folder up of the given link"
    import os
    parent_link = ""
    if(os.path.splitext(svn_link)[1] == ""):
        parent_link = svn_link[:-1]
        index = parent_link.rfind("/")
        parent_link = parent_link[:index]
    parent_link = parent_link + "/"
    folder_list = []
    folder_list.append({
        "id": parent_link,
        "parent": "#",
        "text": parent_link,
        "children": [],
        "icon" : "directory.png",
        "children_status":True,
        "public_permission":True, 
        "map_staus": False,
        "size":""
    })
    return folder_list

def get_all_revisions_available(link):
    """ List all the revisions availabel for a particular link
    """
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    link = link.replace("dllohsr222","10.133.0.222")
    args = ["svn", "log",
           link,"--xml",
            "--username", svn_username,
            "--password", svn_password,
            "--non-interactive", "--no-auth-cache"]
    import subprocess
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    #logger.info(out)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(out, "xml")
    revision_data = soup.find_all('logentry')
    #logger.info(revision_data)
    rev_list = []
    for rev in revision_data:
        rev_list.append((int(rev["revision"]),rev.msg.getText()))
    #revision_list = []
    ##for rev in revision_data:
    import operator
    rev_list.sort(key=operator.itemgetter(0), reverse = True)
    updated_rev_list = []
    first_flag = False
    for rev_data in rev_list:
        if not first_flag:
            updated_rev_list.append("{}->{}(Latest)".format(rev_data[0], rev_data[1]))
            first_flag = True
        else:
            updated_rev_list.append("{}->{}".format(rev_data[0], rev_data[1]))
    return updated_rev_list


def check_if_project_is_small(link):
    import os
    parent_link = ""
    is_small = False
    if(os.path.splitext(link)[1] == ""):
        parent_link = link[:-1]
        index = parent_link.rfind("/")
        folder_name = parent_link[index+1:]
        parent_link = parent_link[:index]
        if folder_name[:5].isdigit():
            is_small = True
    return False

def download_the_selected_files(link, folder_path, revision, timestamp, permission = False):
    """ common function to download the given files!
    """
    #logger.debug(link)
    #logger.debug(permission)
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    if permission:
        export_to_the_path(link, folder_path, svn_username,svn_password, revision, True)
    else:
        folders, _ = svnlib.list_folder(
        link , svn_username, svn_password)
        permitted_folders, permitted_files, public_files, public_folders = get_all_permitted_links_in_the_folder(link, folders)
        #logger.debug(permitted_folders)
        #logger.debug(permitted_files)
        permitted_list = []
        permitted_list.extend(permitted_folders)
        permitted_list.extend(permitted_files)
        permitted_list = list(set(permitted_list))
        #logger.debug(permitted_folders)
        #logger.debug(permitted_files)
        export_to_the_path(link, folder_path, svn_username,svn_password, revision, False)
        # Not conventional beware!!
        if link[-1] is "/":
            link = link[:-1]
        #logger.debug(link)
        names = link.split("/") 
        #logger.debug(names)
        folder_name = names[-1]
        #logger.debug(folder_name)
        new_folder_path = os.path.join(folder_path,folder_name)
        #logger.debug(new_folder_path)
        for folder in permitted_folders:
            export_to_the_path(folder, new_folder_path,  svn_username,svn_password , revision, True)
        for files in permitted_files:
            if  files[-1] is "/":
                download_the_selected_files(files, new_folder_path, revision, timestamp, False)
            else:
                export_to_the_path(files, new_folder_path, svn_username,svn_password, revision, False)


def export_to_the_path(link, folder_path, svn_username,svn_password, revision= "", permission= False):
    #logger.debug("Exporting {}".format(link))
    exported_path = ""
    if not permission:
        if revision and len(revision):
            exported_path = svnlib.export(link, folder_path,svn_username,svn_password,depth="empty", revision= revision)
        else:
            exported_path = svnlib.export(link, folder_path,svn_username,svn_password,depth="empty")
    else:
        if revision and len(revision):
            exported_path = svnlib.export(link, folder_path,svn_username,svn_password, revision= revision)
        else:
            exported_path = svnlib.export(link, folder_path,svn_username,svn_password)
    return exported_path 

def write_public_data_for_given_links(issue_id, selected_links):
    """ Get the link for the id
    Check if it has public data, if it has then checkout and rename our file and commit
    If not import!
    """
    if not len(selected_links):
        return
    svn_username = current_user.svn_username
    svn_password = current_user.svn_password
    mapped_obj = Mapping.get_mapping_for(issue_id)
    current_link = mapped_obj.link
    instance_path = current_app.instance_path
    #folders, _ = svnlib.list_folder(current_link , svn_username, svn_password)
    import datetime
    timestamp = datetime.datetime.utcnow()
    timestamp = str(timestamp).replace("/","_").replace(":","_").replace(" ","_").replace(",","").replace(".","").replace("-","_")
    from result_linker.models.public import Public
    #data_folder = os.path.join(instance_path, "write_data_{}".format(timestamp))
    #os.mkdir(data_folder)
    public_folder = []
    public_files = []
    for link in selected_links:
        if link[-1] is "/":
            public_folder.append(link)
        else:
            public_files.append(link)
    public_folder_str="||".join(str(x) for x in public_folder)
    public_files_str="||".join(str(x) for x in public_files)
    Public.make_public(issue_id, current_link, public_folder_str, public_files_str, svn_username)
    #import json
    #json_path = os.path.join(data_folder,"public_data.json")
    #json_data = {}
    #json_data["public_files"] = public_files
    #json_data["public_folders"] = public_folder
    #with open(json_path, 'w+',  encoding='utf-8') as json_file:
    #    json_file.write(json.dumps(json_data, ensure_ascii=False, indent=4))
    #if "public_data.json" in folders:
    #    logger.debug("Checking out exisitng public data json")
    #    checkout_path = os.path.join(data_folder,"checkout")
    #    checkout_path += os.sep
    #    os.mkdir(checkout_path)
    #    if current_link[-1] is not "/":
    #         current_link = current_link + "/"
    #    err = svnlib.checkout(current_link, checkout_path, svn_username, svn_password, depth="files")
    #    link_parts = current_link.split("/")
    #    copy_path = os.path.join(checkout_path,link_parts[-2])
    #    #logger.debug(copy_path)
    #    new_json_path = os.path.join(copy_path, "public_data.json")
    #    import shutil
    #    shutil.copy2(json_path, new_json_path)
    #    errs = svnlib.commit(copy_path, svn_username, svn_password, file_name= new_json_path,
    #                            commit_message="Updated the public data .json through result linker tool")
    #    logger.debug(errs)                        
    #else:
    #    logger.debug("Adding new public data json")
    #    if current_link[-1] is not "/":
    #         current_link = current_link + "/"
    #    current_link += "public_data.json"
    #    svnlib.import_item(current_link,json_path,svn_username,svn_password,"Introduced public data through result linker")
    #import shutil
    #if os.path.exists(data_folder):
    #    shutil.rmtree(data_folder)


def get_svn_file_size_for_file(svn_link, svn_username, svn_password, **kwargs):
    """
    Send only file not folders!!!!
    """
    import subprocess
    from bs4 import BeautifulSoup
    args = ["svn", "list","--xml" , svn_link,
            "--username",
            svn_username, "--password",
            svn_password, "--non-interactive",
            "--no-auth-cache"
            ]
    for key in kwargs:
        args.extend(["--{}".format(key), kwargs[key]])
    query_process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    out, err = query_process.communicate()
    out = out.decode("utf-8")
    soup = BeautifulSoup(out, "xml")
    size_data = ""
    try:
        size_data = soup.find("size").get_text()
    except:
        size_data = ""
    if size_data:
        size_data = humanbytes(size_data)
    else:
        size_data = ""
    return size_data


def get_revision_number(rev_string):
    rev_string = str(rev_string)
    revision_number = ""
    revisions_split = []
    if not rev_string:
        return ""
    if rev_string.isnumeric():
        return rev_string
    if len(rev_string):
        revisions_split = rev_string.split("->")
    if(len(revisions_split) > 1):
        revision_number = revisions_split[0]
    else:
        revision_number = ""
    return revision_number

def decode_option(option):
    option_number = int(option)
    if option_number == 1:
        return "preselected_same_revision" 
    elif option_number == 2:
        return "preselected_new_revision" 
    elif option_number == 3:
        return "preselected_all_revision"
    elif option_number == 4:
        return "public_same_revision"
    elif option_number == 5:
        return "public_all_revision"

def create_public_data_for_given_template(issue_id,template_type, svn_username):
    """Create Public data
    """
    from result_linker.models.public import Public
    #data_folder = os.path.join(instance_path, "write_data_{}".format(timestamp))
    #os.mkdir(data_folder)
    mapped_obj = Mapping.get_mapping_for(issue_id)
    svn_link = mapped_obj.link
    public_folder = []
    public_files = []
    if template_type == "AmeSim":
        public_folder.append("{}/trunk/05_Mod/".format(svn_link))
        public_folder.append("{}/trunk/15_Inputs/".format(svn_link))
        public_folder.append("{}/trunk/03_Spec/".format(svn_link))
        public_folder.append("{}/trunk/02_Pres/".format(svn_link))
    elif template_type == "workorder_CAE":
        public_folder.append("{}/_DocuExternal/".format(svn_link))
    elif template_type == "workorder_CAE_minimal":
        public_folder.append("{}/_Report/_SentToExternal/".format(svn_link))
    elif template_type == "workorder_FEA":
        public_folder.append("{}/_DocuExternal/".format(svn_link))
    elif template_type == "workorder_FEA":
        public_folder.append("{}/_DocuExternal/".format(svn_link))   
    public_folder_str="||".join(str(x) for x in public_folder)
    public_files_str="||".join(str(x) for x in public_files)
    Public.make_public(issue_id, svn_link, public_folder_str, public_files_str, svn_username)