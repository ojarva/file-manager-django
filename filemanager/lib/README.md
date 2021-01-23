Helper scripts
==============

permissions.sh
--------------

This script sets permissions for shared folders. Be sure to check what it does before running it. Also, it assumes /home/u/username type naming 
convention.

safe_chown.py
-------------

This is wrapper script for changing file owners. It validates chown requests before running actual commands - for example, chown is only allowed 
under /home.
