# -*- coding: utf-8 -*-
#
# Integration tests for miscellaneous stuff
#

from collective.easyform.tests import base
from plone import api
from plone.namedfile.file import NamedFile
from zope.component import getMultiAdapter


class TestGetEasyFormURL(base.EasyFormTestCase):
    """test GetEasyFormURL stuff"""

    def afterSetUp(self):
        self.folder.invokeFactory("EasyForm", "ff1")
        self.form = self.folder.ff1
        self.form_url = self.form.absolute_url()

    def get_view(self, context):
        request = self.layer["request"]
        return getMultiAdapter((context, request), name="get-easyform-url")

    def check_urls_form(self, view):
        # For a view somewhere in a form
        self.assertEqual(view("fields"), self.form_url + "/fields")
        self.assertEqual(view("/fields"), self.form_url + "/fields")
        self.assertEqual(view("actions"), self.form_url + "/actions")
        self.assertEqual(view(""), self.form_url + "")

    def check_urls_non_form(self, view):
        # For a view outside a form
        self.assertEqual(view("fields"), "./fields")
        self.assertEqual(view("/fields"), "./fields")
        self.assertEqual(view("actions"), "./actions")
        self.assertEqual(view(""), "./")

    def test_get_easyform_url_form(self):
        view = self.get_view(self.form)
        self.check_urls_form(view)

    def test_get_easyform_url_fields(self):
        view = self.get_view(self.form.restrictedTraverse("fields"))
        self.check_urls_form(view)

    def test_get_easyform_url_actions(self):
        view = self.get_view(self.form.restrictedTraverse("actions"))
        self.check_urls_form(view)

    def test_get_easyform_url_folder(self):
        view = self.get_view(self.folder)
        self.check_urls_non_form(view)

    def test_get_easyform_url_portal(self):
        view = self.get_view(self.portal)
        self.check_urls_non_form(view)


class TestIsSubEasyForm(base.EasyFormTestCase):
    """test IsSubEasyForm stuff"""

    def afterSetUp(self):
        self.folder.invokeFactory("EasyForm", "ff1")
        self.form = self.folder.ff1
        self.form_url = self.form.absolute_url()

    def get_view(self, context):
        request = self.layer["request"]
        return getMultiAdapter((context, request), name="is-sub-easyform")

    def test_is_sub_easyform_form(self):
        view = self.get_view(self.form)
        self.assertFalse(view())

    def test_is_sub_easyform_fields(self):
        view = self.get_view(self.form.restrictedTraverse("fields"))
        self.assertTrue(view())

    def test_is_sub_easyform_actions(self):
        view = self.get_view(self.form.restrictedTraverse("actions"))
        self.assertTrue(view())

    def test_is_sub_easyform_folder(self):
        view = self.get_view(self.folder)
        self.assertFalse(view())

    def test_is_sub_easyform_root(self):
        view = self.get_view(self.portal)
        self.assertFalse(view())


class TestCustomTemplates(base.EasyFormTestCase):

    no_schema = u"""
  <model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema></schema>
  </model>
        """

    def test_custom_fields(self):
        default_fields = api.content.create(
            self.portal, "File", id="easyform_default_fields.xml"
        )
        default_fields.file = NamedFile(self.no_schema)
        ef = api.content.create(self.folder, "EasyForm", id="my-form")
        self.assertEqual(ef.fields_model, self.no_schema)

    def test_custom_actions(self):
        default_actions = api.content.create(
            self.portal, "File", id="easyform_default_actions.xml"
        )
        default_actions.file = NamedFile(self.no_schema)
        ef = api.content.create(self.folder, "EasyForm", id="my-form")
        self.assertEqual(ef.actions_model, self.no_schema)
