"""
This file contains methods for managing files and other helper classes, like formatters.
"""

import shutil
import os
import glob
import subprocess
from datetime import datetime


class FileOperations:
    """ FileOperations class is used for handling file operations """

    def __init__(self):
        pass

    @staticmethod
    def construct_fullpath_raw(user, *args):
        """ returns full path without any validation """
        fullpath = "/home/%s/%s" % (user[0], user)
        for arg in args:
            if len(arg) > 0:
                fullpath = "%s/%s" % (fullpath, arg)
        return fullpath

    @staticmethod
    def construct_fullpath(user, *args):
        """ constructs full path from args. Returns path if path doesn't
        contain symbolic links or None if something fails.
        """

        path = FileOperations.construct_fullpath_raw(user, *args)

        """ As all file operations run using separate filemanager
        user, symbolic links (and hard links too) are too dangerous

        Resolving realpath and comparing it to original path
        shows symbolic links, but doesn't help against hardlinks.
        """
        fullpath = os.path.realpath(path)
        if path != fullpath:
            return None
        return fullpath

    @staticmethod
    def valid_file(user, *args):
        """ Return True if file exists and path doesn't contain any symbolic links,
        False otherwise.
        """
        fullpath = FileOperations.construct_fullpath(user, *args)
        if not fullpath or not os.path.exists(fullpath):
            return False
        return True

    @staticmethod
    def save_permissions(user, folder, path, settings):
        fullpath = FileOperations.construct_fullpath(user, folder, path)
        if not fullpath:
            return {"success": False, "status": "No symlinks are allowed"}

        if not os.path.isdir(fullpath):
            return {"success": False, "status": "Path is not directory"}

        mode = settings.get("mode", "public")
        if mode == "public":
            # Clean up authentication configurations 
            try:
                os.remove(fullpath+"/.htaccess")
            except:
                pass
            try:
                os.remove(fullpath+"/.htpasswd")
            except:
                pass
            return {"success": True}

        if mode == "sso":
            contents = """Order deny,allow
Deny from all
Satisfy any
AuthType mod_auth_pubtkt
TKTAuthLoginURL https://login.futurice.com/
TKTAuthTimeoutURL https://login.futurice.com/?timeout=1
TKTAuthUnauthURL https://login.futurice.com/?unauth=1
TKTAuthToken "futu"
TKTAuthToken "ext"
Require valid-user"""
            open(fullpath+"/.htaccess", "w").write(contents)
            FileOperations.chown(user, fullpath+"/.htaccess")
            return {"success": True}

        if mode == "basicauth":
            contents = """AuthType Basic
AuthName "Protected files"
AuthUserFile %s
Require valid-user""" % (fullpath+"/.htpasswd")
            open(fullpath+"/.htaccess", "w").write(contents)
            FileOperations.chown(user, fullpath+"/.htaccess")
            p = subprocess.Popen(["htpasswd", "-cbs", fullpath+"/.htpasswd", settings.get("username"), settings.get("password")])
            p.wait()
            return {"success": True}

        return {"success": False, "status": "Invalid method"}


    @staticmethod
    def get_file(user, *args):
        """ Get details for single file """
        fullpath = FileOperations.construct_fullpath(user, *args)
        if not fullpath:
            return {}
        return FileOperations.get_file_raw(fullpath)

    @staticmethod
    def get_file_raw(file):
        """ Get details for single file. Argument is filename. """

        type = "unknown"
        if os.path.isfile(file):
            type = "file"
        elif os.path.isdir(file):
            type = "dir"
        elif os.path.islink(file):
            type = "link"
        size = os.path.getsize(file)
        mtime = os.path.getmtime(file)
        mtime_readable = pretty_date(mtime)
        return {"full_path": file, "filename": os.path.basename(file), "size": size, "type": type, "mtime": mtime, "mtime_readable": mtime_readable}

    @staticmethod
    def get_files(user, folder, path):
        """ Get details for files inside folder """
        fullpath = FileOperations.construct_fullpath(user, folder, path)
        if not fullpath:
            return []

        if not os.path.isdir(fullpath):
            return []

        list_of_files = glob.glob("%s/*" % fullpath)
        list_of_files.sort()
        files_final = []
        for file in list_of_files:
            files_final.append(FileOperations.get_file_raw(file))
        return files_final

    @staticmethod
    def chown(user, fullpath):
        """ Change ownership for single file or folder (non-recursive). """
        p = subprocess.Popen(["sudo", "/root/safe_chown.py", user, fullpath])
        p.wait()

    @staticmethod
    def mkdir(user, folder, path, foldername):
        """ Create new directory """
        fullpath = FileOperations.construct_fullpath(user, folder, path, foldername)
        if not fullpath:
            return {"success": False, "status": "Invalid path (contains symbolic links)"}

        if os.path.exists(fullpath):
            return {"success": False, "status": "File already exists"}
        os.mkdir(fullpath, 0771)
        FileOperations.chown(user, fullpath)
        return {"success": True}

    @staticmethod
    def delete_file(user, folder, path):
        fullpath = FileOperations.construct_fullpath(user, folder, path)
        if fullpath and os.path.exists(fullpath):
            try:
                if os.path.isdir(fullpath):
                    shutil.rmtree(fullpath)
                else:
                    os.remove(fullpath)
                return {"success": True}
            except Exception, e:
                return {"success": False, "status": "rm failed: %s" % fullpath, "err": str(e)}
        return {"success": False, "status": "No such file or directory"}

    @staticmethod
    def upload_file(f, user, folder, path):
        """ Upload new file """
        fullpath = FileOperations.construct_fullpath(user, folder, path, f.name)
        if not fullpath:
            return False
        destination = open(fullpath, "wb")
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        FileOperations.chown(user, fullpath)


# from http://stackoverflow.com/a/1551394/592174
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    if type(time) is int or type(time) is float:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"
