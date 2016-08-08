# -*- coding: utf-8 -*-
#
# Test PFG -> EasyForm migration
#
# Run this test only: bin/test -s collective.easyform -t testPFGmigration
#

from collective.easyform.tests import base
from plone.testing import z2
from collective.easyform.migrations import migrate_pfg_content

try:
    import Products.PloneFormGen
    HAVE_PFG = True
except ImportError:
    HAVE_PFG = False


class MyFixture(base.Fixture):

    defaultBases = (base.PLONE_FIXTURE,)

    def setUpZope(self, app, configuration_context):
        super(MyFixture, self).setUpZope(app, configuration_context)
        try:
            self.loadZCML(
                package=Products.PloneFormGen, context=configuration_context)
            z2.installProduct(app, 'Products.PloneFormGen')
        except ImportError:
            pass

    def setUpPloneSite(self, portal):
        super(MyFixture, self).setUpPloneSite(portal)
        self.applyProfile(portal, 'Products.PloneFormGen:default')


INTEGRATION_TESTING = base.IntegrationTesting(
    bases=(MyFixture(),),
    name='collective.easyform:PFGMigration',
)


class MigrationFormTestCase(base.EasyFormTestCase):

    layer = INTEGRATION_TESTING


class TestPFGmigration(MigrationFormTestCase):

    """ test migration from PloneFormGen """

    def afterSetUp(self):
        super(TestPFGmigration, self).afterSetUp()
        self.folder.invokeFactory('EasyForm', 'ef1')
        self.ef1 = getattr(self.folder, 'ef1')
        self.folder.invokeFactory('FormFolder', 'pfgff1')
        self.pfgff1 = getattr(self.folder, 'pfgff1')
        # PFG Forms are born with sample fields: two strings and a text field.
        # We'll want to try all the PFG fields that we can support

    def testHaveBothForms(self):
        object_ids = sorted(self.folder.objectIds())
        self.assertEqual(object_ids, ['ef1', 'pfgff1'])
        self.assertEqual(self.ef1.portal_type, 'EasyForm')
        self.assertEqual(self.pfgff1.portal_type, 'FormFolder')

    def testStringField(self):
        transformed_string = migrate_pfg_content(self.pfgff1)
        expected = '<field name="reply_to" type="zope.schema.Field"/><field name="topic" type="zope.schema.Field"/>'
        self.assertEquals(transformed_string, expected)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if HAVE_PFG:
        suite.addTest(makeSuite(TestPFGmigration))
    return suite
