#
# Integration tests for interaction with GenericSetup infrastructure
#

from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.formulator import content
from collective.formulator import interfaces
from collective.formulator.tests import base


class TestFormGenInterfaces(base.FormulatorTestCase):

    """ Some boilerplate-ish tests to confirm that that classes
        and instances confirm to the interface contracts intended.
    """

    def afterSetUp(self):
        base.FormulatorTestCase.afterSetUp(self)

        # add form folder for use in tests
        self.folder.invokeFactory('Formulator', 'ff1')

    def testBrowserViewClassInterfaces(self):
        """Some basic boiler plate testing of interfaces and classes"""
        # verify IFormulatorExportView
        # self.assertTrue(
            # interfaces.IFormulatorExportView.implementedBy(exportimport.FormulatorExportView))
        # self.assertTrue(
            # verifyClass(interfaces.IFormulatorExportView,
            # exportimport.FormulatorExportView))

    def testBrowserViewObjectsVerify(self):
        # verify views are objects of the expected class, verified
        # implementation
        form_folder_export = getMultiAdapter(
            (self.folder.ff1, self.app.REQUEST), name='export-form-folder')
        # self.assertTrue(isinstance(
            # form_folder_export, exportimport.FormulatorExportView))
        self.assertTrue(verifyObject(interfaces.IFormulatorExportView,
                        form_folder_export))

    def testContentClassInterfaces(self):
        self.assertTrue(
            interfaces.IFormulatorFieldset.implementedBy(content.fieldset.FieldsetFolder))
        self.assertTrue(
            verifyClass(interfaces.IFormulatorFieldset, content.fieldset.FieldsetFolder))


def test_suite():
    from unittest import TestSuite  # , makeSuite
    suite = TestSuite()
    # suite.addTest(makeSuite(TestFormGenInterfaces))
    return suite
