# -*- coding: utf-8 -*-
from collective.easyform.tests.base import FUNCTIONAL_TESTING
from plone import api
from plone.testing import layered
from plone.testing.z2 import Browser

import doctest
import re
import six
import transaction
import unittest


optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE
    | doctest.NORMALIZE_WHITESPACE
    | doctest.ELLIPSIS
    | doctest.REPORTING_FLAGS
)

testfiles = (
    "browser.rst",
    "attachment.rst",
    "ssl.txt",
    "serverside_field.txt",
    "../api.py",
    "../README.txt",
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
        api.user.create(
            username="adm", password="secret", email="a@example.org", roles=("Manager",)
        )
        transaction.commit()
        browser.addHeader("Authorization", "Basic adm:secret")
    return browser


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    f,
                    optionflags=optionflags,
                    globs={"get_browser": get_browser},
                    checker=Py23DocChecker(),
                ),
                layer=FUNCTIONAL_TESTING,
            )
            for f in testfiles
        ]
    )
    return suite
