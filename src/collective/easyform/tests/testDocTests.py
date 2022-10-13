# -*- coding: utf-8 -*-
from collective.easyform.tests.base import FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import layered
from plone.testing.zope import Browser

import doctest
import os
import re
import six
import unittest


LINESEP = b"\r\n"

optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE
    | doctest.NORMALIZE_WHITESPACE
    | doctest.ELLIPSIS
    | doctest.REPORTING_FLAGS
)

testfiles = (
    "../api.py",
    "attachment.rst",
    "basic.rst",
    "browser.rst",
    "serverside_field.rst",
    "ssl.rst",
    "action_errors.rst",
)


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub("zExceptions.NotFound", "NotFound", got)
            got = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def get_browser(layer, auth=True):
    browser = Browser(layer["app"])
    browser.handleErrors = False
    if auth:
        browser.open('http://nohost/plone/login_form')
        browser.getControl('Login Name').value = SITE_OWNER_NAME
        browser.getControl('Password').value = SITE_OWNER_PASSWORD
        browser.getControl('Log in').click()
    return browser


def get_image_path():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    return "{0}/PloneLogo.png".format(dir_name)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    f,
                    optionflags=optionflags,
                    globs={
                        "LINESEP": LINESEP,
                        "get_browser": get_browser,
                        "get_image_path": get_image_path,
                    },
                    checker=Py23DocChecker(),
                ),
                layer=FUNCTIONAL_TESTING,
            )
            for f in testfiles
        ]
    )
    return suite
