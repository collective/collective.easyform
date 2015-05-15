# -*- coding: utf-8 -*-
#
# Integration tests for interaction with GenericSetup infrastructure
#

from collective.easyform import content
from collective.easyform import interfaces
from collective.easyform.tests import base
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestFormGenInterfaces(base.EasyFormTestCase):

    """ Some boilerplate-ish tests to confirm that that classes
        and instances confirm to the interface contracts intended.
    """

    def afterSetUp(self):
        base.EasyFormTestCase.afterSetUp(self)

        # add form folder for use in tests
        self.folder.invokeFactory('EasyForm', 'ff1')

    def testBrowserViewClassInterfaces(self):
        """Some basic boiler plate testing of interfaces and classes"""
        # verify IEasyFormExportView
        # self.assertTrue(
        #     interfaces.IEasyFormExportView.implementedBy(exportimport.EasyFormExportView))
        # self.assertTrue(
        #     verifyClass(interfaces.IEasyFormExportView,
        #     exportimport.EasyFormExportView))

    def testBrowserViewObjectsVerify(self):
        # verify views are objects of the expected class, verified
        # implementation
        form_folder_export = getMultiAdapter(
            (self.folder.ff1, self.app.REQUEST), name='export-form-folder')
        # self.assertTrue(isinstance(
        #     form_folder_export, exportimport.EasyFormExportView))
        self.assertTrue(verifyObject(interfaces.IEasyFormExportView,
                        form_folder_export))

    def testContentClassInterfaces(self):
        self.assertTrue(
            interfaces.IEasyFormFieldset.implementedBy(content.fieldset.FieldsetFolder))
        self.assertTrue(
            verifyClass(interfaces.IEasyFormFieldset, content.fieldset.FieldsetFolder))


def test_suite():
    from unittest import TestSuite  # , makeSuite
    suite = TestSuite()
    # suite.addTest(makeSuite(TestFormGenInterfaces))
    return suite
