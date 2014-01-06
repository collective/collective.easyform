#
# Test PloneFormGen event-handler functionality
#

#import os
#import sys

from collective.formulator.tests import pfgtc
from collective.formulator.api import get_actions, get_fields

#if __name__ == '__main__':
    #execfile(os.path.join(sys.path[0], 'framework.py'))


class TestAdapterPaste(pfgtc.PloneFormGenTestCase):

    """Ensure content types can be created and edited"""

    adapterTypes = (
        'FormSaveDataAdapter',
        'FormMailerAdapter',
        'FormCustomScriptAdapter',
    )

    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)
        self.folder.invokeFactory('Formulator', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testActiveAdaptersNotDuplicatedOnFormCopy(self):
        self.loginAsPortalOwner()
        copy = self.folder.manage_copyObjects('ff1')
        new_id = self.folder.manage_pasteObjects(copy)[0]['new_id']
        ff2 = getattr(self.folder, new_id)
        active_adapters = tuple(get_actions(ff2))
        self.assertEqual(active_adapters, ('mailer',))
        active_fields = tuple([i for i in get_fields(ff2)])
        self.assertEqual(active_fields, ('replyto', 'topic', 'comments'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapterPaste))
    return suite
