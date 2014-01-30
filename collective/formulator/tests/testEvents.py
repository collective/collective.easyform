#
# Test Formulator event-handler functionality
#

from collective.formulator.tests import base
from collective.formulator.api import get_actions, get_fields


class TestAdapterPaste(base.FormulatorTestCase):

    """Ensure content types can be created and edited"""

    adapterTypes = (
        'FormSaveDataAdapter',
        'FormMailerAdapter',
        'FormCustomScriptAdapter',
    )

    def afterSetUp(self):
        super(TestAdapterPaste, self).afterSetUp()
        self.folder.invokeFactory('Formulator', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testActiveAdaptersNotDuplicatedOnFormCopy(self):
        # self.loginAsPortalOwner()
        copy = self.folder.manage_copyObjects('ff1')
        new_id = self.folder.manage_pasteObjects(copy)[0]['new_id']
        ff2 = getattr(self.folder, new_id)
        active_adapters = tuple(get_actions(ff2))
        self.assertEqual(active_adapters, ('mailer',))
        active_fields = tuple(get_fields(ff2))
        self.assertEqual(active_fields, ('replyto', 'topic', 'comments'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapterPaste))
    return suite
