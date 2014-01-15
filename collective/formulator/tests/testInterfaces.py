#
# Integration tests for interaction with GenericSetup infrastructure
#

#import os
#import sys
# if __name__ == '__main__':
    #execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.interface.verify import verifyObject, verifyClass
from zope.component import getMultiAdapter

from collective.formulator.tests import base
from collective.formulator import interfaces
#from collective.formulator.browser import exportimport
from collective.formulator import content


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


# if __name__ == '__main__':
    # framework()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # suite.addTest(makeSuite(TestFormGenInterfaces))
    return suite
