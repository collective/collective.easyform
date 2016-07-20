# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from collective.easyform.tests.base import EasyFormFunctionalTestCase
# from plone.testing import layered
import doctest
import unittest2 as unittest

optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE |
    doctest.NORMALIZE_WHITESPACE |
    doctest.ELLIPSIS |
    doctest.REPORTING_FLAGS)

testfiles = (
    'browser.txt',
    'attachment.txt',
    'ssl.txt',
    'serverside_field.txt',
    '../api.py',
    '../README.txt',
)


def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            f, package='collective.easyform.tests',
            test_class=EasyFormFunctionalTestCase,
            optionflags=optionflags)
        for f in testfiles
    ])
