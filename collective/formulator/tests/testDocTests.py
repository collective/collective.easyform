import doctest
import unittest2 as unittest
#from plone.testing import layered
from Testing import ZopeTestCase as ztc
from collective.formulator.tests.base import FormulatorFunctionalTestCase

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

#formulatorfunctionaltestcase = FormulatorFunctionalTestCase()
# def setUp(test):
    # formulatorfunctionaltestcase.setUp()
# def tearDown(test):
    # formulatorfunctionaltestcase.tearDown()

# def test_suite():
    #suite = unittest.TestSuite()
    # suite.addTests([
        # layered(doctest.DocFileSuite(test,
                                     # optionflags=optionflags,
                                     # setUp=setUp,
                                     # tearDown=tearDown,
                                     #),
                # layer=FormulatorFunctionalTestCase.layer)
        # for test in testfiles])
    # return suite


def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            f, package='collective.formulator.tests',
            test_class=FormulatorFunctionalTestCase,
            optionflags=optionflags)
        for f in testfiles
    ])
