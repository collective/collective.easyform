import unittest
import doctest

from Testing import ZopeTestCase as ztc
from collective.formulator.tests.base import FormulatorFunctionalTestCase

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
            f, package='collective.formulator.tests',
            test_class=FormulatorFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORTING_FLAGS)

        for f in testfiles
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
