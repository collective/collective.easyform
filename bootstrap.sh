#!/bin/sh

# see https://community.plone.org/t/not-using-bootstrap-py-as-default/620
# rm -r ./lib ./include ./local ./bin
python3 -m venv venv --clear
./venv/bin/pip install -r requirements.txt
./venv/bin/buildout bootstrap
