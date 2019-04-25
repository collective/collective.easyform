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


class TestMisc(base.EasyFormTestCase):
    """ test miscellaneous stuff """

    def test_ordereddict_reverse(self):
        d = OrderedDict()
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3
        self.assertEqual(d.reverse(), [("c", 3), ("b", 2), ("a", 1)])


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
