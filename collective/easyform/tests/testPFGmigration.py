# -*- coding: utf-8 -*-
#
# Test PFG -> EasyForm migration
#
# Run this test only: bin/test -s collective.easyform -t testPFGmigration
#

# from collective.easyform.migrations import migrate_pfg_content
from collective.easyform.migrations import migrate_pfg_string_field, migrate_pfg_content
from collective.easyform.tests import base
from plone.supermodel import serializeSchema
# from plone.supermodel.model import SchemaClass
from plone.schemaeditor.interfaces import IEditableSchema
from plone.testing import z2
from zope.interface import Interface

import re

try:
    import Products.PloneFormGen
    HAVE_PFG = True
except ImportError:
    HAVE_PFG = False


SUBJECT_FIELD_XML = u'''<field name="topic" type="zope.schema.TextLine"> <title>Subject</title> </field>'''


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


def serializeField(afield, name):
    # return an XML serialization of an individual field,
    # normalize for spacing, eols

    class TestClass(Interface):
        pass
    schema = TestClass
    IEditableSchema(TestClass).addField(afield, name=name)
    s = serializeSchema(schema)
    found = re.findall('<field.+?</field>', s.replace('\n', ' '))
    if len(found) == 1:
        return re.sub(u' +', ' ', found[0])
    return u''


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
        expected = '<field name="replyto" type="zope.schema.Field" /><field name="topic" type="zope.schema.Field" />'
        self.assertEquals(transformed_string, expected)

    def testStringFieldConversion(self):
        sample_pfg_string_field = self.pfgff1.topic
        tsf = migrate_pfg_string_field(sample_pfg_string_field)
        self.assertEqual(SUBJECT_FIELD_XML, serializeField(tsf, name=u'topic'))

    def testNonRequiredFieldConversion(self):
        sample_pfg_string_field = self.pfgff1.topic
        sample_pfg_string_field.setRequired(False)
        tsf = migrate_pfg_string_field(sample_pfg_string_field)
        self.assertTrue(u'<required>False</required>' in serializeField(tsf, name=u'topic'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if HAVE_PFG:
        suite.addTest(makeSuite(TestPFGmigration))
    return suite
