#!/bin/bash

#This must be run from a virtualenv that has the requirements for resgate isntalled already
echo $PWD $0
if [ "$0" == './webserver.sh' ] ; then
    echo "Don't run this from the bin/ directory"
    exit 1
fi
pip install -U -r requirements-test.py
pip install -U -r requirements-dev.py
pip install -U -r requirements.py
pip install -U -e .
adev runserver lib/webserver_buttontest.py
    
# echo "Not using sanic for now, using aiohttp to try out pywebio so use"
# echo "run_webserver.sh"
# exit  1
# exec sanic lib.webserver.app
