# -*- coding: utf-8 -*-
#
# Integration tests for miscellaneous stuff
#

from AccessControl import Unauthorized
from collective.easyform.actions import OrderedDict
from collective.easyform.browser.fields import AjaxSaveHandler
from collective.easyform.tests import base
from plone import api
from plone.namedfile.file import NamedFile
from zope.component import getMultiAdapter


class TestMisc(base.EasyFormTestCase):
    """ test miscellaneous stuff """

    def test_ordereddict_reverse(self):
        d = OrderedDict()
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3
        self.assertEqual(d.reverse(), [("c", 3), ("b", 2), ("a", 1)])

    def test_default_values_translated(self):
        self.layer["request"]["LANGUAGE"] = "de"
        self.folder.invokeFactory("EasyForm", "ff1")
        # Check if the submitLabel is translated at all.
        # If you ever change the german translation of the submit label, change it here also
        self.assertEqual(self.folder.ff1.submitLabel, "Absenden")


class TestGetEasyFormURL(base.EasyFormTestCase):
    """ test GetEasyFormURL stuff """

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
    """ test IsSubEasyForm stuff """

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


class TestAjaxSaveHandler(base.EasyFormTestCase):
    def test_ajax_save_handler_call_unathorized(self):
        self.folder.invokeFactory("EasyForm", "ff1")
        view = AjaxSaveHandler(self.folder["ff1"], self.layer["request"])
        with self.assertRaises(Unauthorized):
            view()


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
