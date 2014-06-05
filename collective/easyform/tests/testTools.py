# -*- coding: utf-8 -*-
#
# Test EasyForm top-level functionality
#

from Products.CMFCore.utils import getToolByName
from collective.easyform.tests import base


class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs


class TestTools(base.EasyFormTestCase):

    """ test our tool """

    def test_FormGenTool(self):
        fgt = getToolByName(self.portal, 'formgen_tool')

        # pt = getToolByName(
        #    self.portal, 'portal_properties').easyform_properties

        fgt.setDefault('permissions_used', ['test text'])
        fgt.setDefault('mail_template', 'something')
        fgt.setDefault('mail_body_type', 'text')
        fgt.setDefault('mail_recipient_email', 'eggs')
        fgt.setDefault('mail_recipient_name', 'spam')
        fgt.setDefault('mail_cc_recipients', ['spam and eggs'])
        fgt.setDefault('mail_bcc_recipients', ['eggs and spam'])
        fgt.setDefault('mail_xinfo_headers', ['one', 'two'])
        fgt.setDefault('mail_add_headers', ['three', 'four'])
        fgt.setDefault('csv_delimiter', '|')

        permits = fgt.getPfgPermissions()
        self.assertTrueEqual(len(permits), 1)
        self.assertTrueEqual(permits[0], 'test text')

        self.assertTrueEqual(fgt.getDefaultMailTemplateBody(), 'something')
        self.assertTrueEqual(fgt.getDefaultMailBodyType(), 'text')
        self.assertTrueEqual(fgt.getDefaultMailRecipient(), 'eggs')
        self.assertTrueEqual(fgt.getDefaultMailRecipientName(), 'spam')
        self.assertTrueEqual(fgt.getCSVDelimiter(), '|')

        cc = fgt.getDefaultMailCC()
        self.assertTrueEqual(len(cc), 1)
        self.assertTrueEqual(cc[0], 'spam and eggs')

        bcc = fgt.getDefaultMailBCC()
        self.assertTrueEqual(len(bcc), 1)
        self.assertTrueEqual(bcc[0], 'eggs and spam')

        xi = fgt.getDefaultMailXInfo()
        self.assertTrueEqual(len(xi), 2)
        self.assertTrueEqual(xi[0], 'one')

        xi = fgt.getDefaultMailAddHdrs()
        self.assertTrueEqual(len(xi), 2)
        self.assertTrueEqual(xi[0], 'three')

    def test_toolRolesForPermission(self):
        fgt = getToolByName(self.portal, 'formgen_tool')

        # make sure rolesForPermission works
        roleList = fgt.rolesForPermission('EasyForm: Add Content')
        self.assertNotEqual(len(roleList), 0)
        mid = ''
        oid = ''
        for role in roleList:
            if role['label'] == 'Manager':
                self.assertTrueEqual(role['checked'], 'CHECKED')
                mid = role['id']
            if role['label'] == 'Owner':
                self.assertTrueEqual(role['checked'], 'CHECKED')
                oid = role['id']
        self.assertTrue(mid)
        self.assertTrue(oid)

        # let's try changing a permission

        # first, get the request ids
        roleList = fgt.rolesForPermission('EasyForm: Edit Advanced Fields')
        self.assertNotEqual(len(roleList), 0)
        mid = ''
        oid = ''
        for role in roleList:
            if role['label'] == 'Manager':
                self.assertTrueEqual(role['checked'], 'CHECKED')
                mid = role['id']
            if role['label'] == 'Owner':
                self.assertTrueEqual(role['checked'], None)
                oid = role['id']
        self.assertTrue(mid)
        self.assertTrue(oid)

        fr = FakeRequest()
        fr.form[mid] = '1'
        fr.form[oid] = '1'
        fr.form['EasyForm: Edit Advanced Fields'] = '1'
        fgt.setRolePermits(fr)

        # now, check to see if it took
        roleList = fgt.rolesForPermission('EasyForm: Edit Advanced Fields')
        self.assertNotEqual(len(roleList), 0)
        mid = ''
        oid = ''
        for role in roleList:
            if role['label'] == 'Manager':
                self.assertTrueEqual(role['checked'], 'CHECKED')
                mid = role['id']
            if role['label'] == 'Owner':
                self.assertTrueEqual(role['checked'], 'CHECKED')
                oid = role['id']
        self.assertTrue(mid)
        self.assertTrue(oid)


def test_suite():
    from unittest import TestSuite  # , makeSuite
    suite = TestSuite()
    # suite.addTest(makeSuite(TestTools))
    return suite
