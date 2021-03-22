#!/bin/bash

#This must be run from a virtualenv that has the requirements for resgate isntalled already

exec sanic lib.webserver.app
