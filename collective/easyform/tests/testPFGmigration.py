# -*- coding: utf-8 -*-
#
# Test PFG -> EasyForm migration
#
# Run this test only: bin/test -s collective.easyform -t testPFGmigration
#

from collective.easyform.migrations import add_pfg_field_to_schema
from collective.easyform.tests import base
from plone.supermodel import serializeSchema
# from plone.supermodel.model import SchemaClass
from plone.testing import z2
from zope.interface import Interface

import re

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


def serializeField(schema):
    # return an XML serialization of an individual field,
    # normalize for spacing, eols

    s = serializeSchema(schema)
    found = re.findall('<field.+?</field>', s.replace('\n', ' '))
    if len(found) == 1:
        return re.sub(u' +', ' ', found[0])
    return u''


def emptySchema():
    class TestClass(Interface):
        pass
    return TestClass


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

    def testStringFieldConversion(self):
        sample_pfg_string_field = self.pfgff1.replyto
        schema = emptySchema()
        add_pfg_field_to_schema(schema, sample_pfg_string_field, name=u'replyto')
        expected = """<field name="replyto" type="zope.schema.TextLine" easyform:TDefault="here/memberEmail" easyform:TValidator="python:False" easyform:serverSide="False" easyform:validators="isEmail"> <default>dynamically overridden</default> <max_length>255</max_length> <title>Your E-Mail Address</title> </field>"""
        self.assertEqual(expected, serializeField(schema))

    def testTextFieldConversion(self):
        sample_pfg_field = self.pfgff1.comments
        sample_pfg_field.setFgDefault('Now is the\ntime.')
        schema = emptySchema()
        add_pfg_field_to_schema(schema, sample_pfg_field, name=u'comments')
        expected = u"""<field name="comments" type="zope.schema.Text" easyform:TValidator="python:False" easyform:serverSide="False"> <default>Now is the time.</default> <title>Comments</title> </field>"""
        self.assertEqual(expected, serializeField(schema))

    def testIntFieldConversion(self):
        self.pfgff1.invokeFactory('FormIntegerField', 'intfield')
        sample_pfg_field = self.pfgff1['intfield']
        sample_pfg_field.fgField.__name__ = 'intfield'
        sample_pfg_field.setMinval(1)
        sample_pfg_field.setMaxval(100)
        sample_pfg_field.setFgDefault('3')
        schema = emptySchema()
        add_pfg_field_to_schema(schema, sample_pfg_field, name=u'intfield')
        expected = u"""<field name="intfield" type="zope.schema.Int" easyform:TValidator="python:False"> <default>3</default> <max>100</max> <min>1</min> <required>False</required> </field>"""
        self.assertEqual(expected, serializeField(schema))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if HAVE_PFG:
        suite.addTest(makeSuite(TestPFGmigration))
    return suite
