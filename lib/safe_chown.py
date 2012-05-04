#!/usr/bin/env python
"""
This is wrapper script for running chown a little bit more safely.

Copy this to folder where only root have write access.

Assuming you are running Django application under user "filemanager",
add line

filemanager   ALL=NOPASSWD: /root/safe_chown.py

to sudoers using visudo.

"""

import subprocess
import os
import sys

if len(sys.argv) < 2:
    print "Syntax: %s <username> <filename>" % sys.argv[0]
    sys.exit(1)

username = sys.argv[1]
filename = sys.argv[2]

if username == "root":
    print "Invalid username."
    sys.exit(2)


filename_tmp = filename.replace("../", "/").replace("//", "/").split("/")
if not (len(filename_tmp) > 4 and filename_tmp[1] == "home" and len(filename_tmp[2]) == 1 and len(filename_tmp[3]) > 3):
    print "Invalid path"
    sys.exit(3)

if not os.path.exists(filename):
    print "File doesn't exist"
    sys.exit(4)

if os.path.islink(filename):
    print "File is symbolic link"

p = subprocess.Popen(["chown", username, filename])
p.wait()
if p.returncode != 0:
    sys.exit(p.returncode)
