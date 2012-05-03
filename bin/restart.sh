#!/bin/bash

# Replace these three settings.
PROJDIR="/home/filemanager"
PIDFILE="$PROJDIR/filemanager.pid"
SOCKET="$PROJDIR/filemanager.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

/usr/bin/env - \
  PYTHONPATH="../python:.." \
  ./manage.py runfcgi --settings=filemanager.settings socket=$SOCKET pidfile=$PIDFILE workdir=$PROJDIR

chmod a+w $SOCKET
