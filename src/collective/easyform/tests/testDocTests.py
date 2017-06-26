# -*- coding: utf-8 -*-
from collective.easyform.tests.base import FUNCTIONAL_TESTING
from plone import api
from plone.testing import layered
from plone.testing.z2 import Browser

import doctest
import transaction
import unittest


optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE |
    doctest.NORMALIZE_WHITESPACE |
    doctest.ELLIPSIS |
    doctest.REPORTING_FLAGS)

testfiles = (
    'browser.rst',
    'attachment.rst',
    'ssl.txt',
    'serverside_field.txt',
    '../api.py',
    '../README.txt',
)


def get_browser(layer):
    api.user.create(
        username='adm', password='secret', email='a@example.org',
        roles=('Manager', )
    )
    transaction.commit()
    browser = Browser(layer['app'])
    browser.addHeader('Authorization', 'Basic adm:secret')
    return browser


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                f,
                optionflags=optionflags,
                globs={'get_browser': get_browser, }
            ),
            layer=FUNCTIONAL_TESTING
        )
        for f in testfiles])
    return suite
