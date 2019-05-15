#!/bin/sh

# see https://community.plone.org/t/not-using-bootstrap-py-as-default/620
rm -r ./lib ./include ./local ./bin
virtualenv --python=python2.7 --clear .
./bin/pip install -r requirements.txt
./bin/buildout
