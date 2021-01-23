#!/bin/sh
# This is what we use to set /home permissions correctly - users can write to home folders using ssh
# or with web UI.
# This script assumes /home/u/username type paths for home folders.

cd /home || exit 1

# Use "filemanager" groups
chgrp filemanager -R ?/*/public_html
chgrp filemanager -R ?/*/public_ssl

# rwx for user, x for group, x for others to home folder (/home/u/username)
chmod 711 ?/*

# rwx for user and group, x for others (to folders)
chmod u+rwx ?/*/public_html
chmod g+rwx ?/*/public_html
chmod o+x ?/*/public_html
chmod u+rwx ?/*/public_ssl
chmod g+rwx ?/*/public_ssl
chmod o+x ?/*/public_ssl

# group and user can write everything to shared folders
chmod g+rw ?/*/public_html/ -R
chmod u+rw ?/*/public_html/ -R

# Set acls for shared folders
setfacl -d -R -m group:filemanager:rwx ?/*/public_html ?/*/public_ssl
setfacl -R -m group:filemanager:rwx ?/*/public_html ?/*/public_ssl
setfacl -d -R -m other:rx ?/*/public_html ?/*/public_ssl
setfacl -R -m other:rx ?/*/public_html ?/*/public_ssl
