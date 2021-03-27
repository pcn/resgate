#!/bin/bash

#This must be run from a virtualenv that has the requirements for resgate isntalled already

echo "Not using sanic for now, using aiohttp to try out pywebio so use"
echo "run_webserver.sh"
exit  1
exec sanic lib.webserver.app
