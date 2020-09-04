# -*- coding: utf-8 -*-
#
# Integration tests specific to the api
#

from collective.easyform.actions import DummyFormView
from collective.easyform.api import filter_fields
from collective.easyform.api import filter_widgets
from collective.easyform.api import get_schema
from collective.easyform.tests import base
from plone import api


class TestFunctions(base.EasyFormTestCase):
    """ Test api """

    def afterSetUp(self):
        super(TestFunctions, self).afterSetUp()
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.dummy_form = DummyFormView(self.ff1, self.layer["request"])
        self.dummy_form.schema = get_schema(self.ff1)
        self.dummy_form.prefix = "form"
        self.dummy_form._update()

    def test_set_fields_updates_modified(self):
        # https://github.com/collective/collective.easyform/issues/8
        # Calling set_fields should update the modification date,
        # also in the catalog.
        from collective.easyform.api import set_fields

        # Gather the original data.
        catalog = api.portal.get_tool("portal_catalog")
        path = "/".join(self.ff1.getPhysicalPath())
        orig_modified = self.ff1.modified()
        brain = catalog.unrestrictedSearchResults(path=path)[0]
        orig_counter = catalog.getCounter()
        self.assertEqual(brain.modified, orig_modified)

        # Set the fields.
        fields = get_schema(self.ff1)
        set_fields(self.ff1, fields)

        # The modification date on the form should have been updated.
        new_modified = self.ff1.modified()
        self.assertGreater(new_modified, orig_modified)

        # The catalog brain should have the new date
        brain = catalog.unrestrictedSearchResults(path=path)[0]
        self.assertEqual(brain.modified, new_modified)
        self.assertGreater(self.ff1.modified(), orig_modified)

        # The catalog counter should have been increased.
        # This helps invalidate caches because the catalogCounter ETag changes.
        self.assertEqual(catalog.getCounter(), orig_counter + 1)

    def test_set_actions_updates_modified(self):
        # https://github.com/collective/collective.easyform/issues/8
        # Calling set_actions should update the modification date,
        # also in the catalog.
        from collective.easyform.api import get_actions
        from collective.easyform.api import set_actions

        # Gather the original data.
        catalog = api.portal.get_tool("portal_catalog")
        path = "/".join(self.ff1.getPhysicalPath())
        orig_modified = self.ff1.modified()
        brain = catalog.unrestrictedSearchResults(path=path)[0]
        orig_counter = catalog.getCounter()
        self.assertEqual(brain.modified, orig_modified)

        # Set the actions.
        actions = get_actions(self.ff1)
        set_actions(self.ff1, actions)

        # The modification date on the form should have been updated.
        new_modified = self.ff1.modified()
        self.assertGreater(new_modified, orig_modified)

        # The catalog brain should have the new date
        brain = catalog.unrestrictedSearchResults(path=path)[0]
        self.assertEqual(brain.modified, new_modified)
        self.assertGreater(self.ff1.modified(), orig_modified)

        # The catalog counter should have been increased.
        # This helps invalidate caches because the catalogCounter ETag changes.
        self.assertEqual(catalog.getCounter(), orig_counter + 1)

    def test_selective_widgets(self):
        """ Test selective inclusion of widgets for mail and thank you page.

        This uses filter_widgets, which needs as input:
        - a context (the form or a mailer)
        - a list of widgets
        """

        self.assertEqual(
            list(filter_widgets(self.ff1, self.dummy_form.w).keys()),
            ["replyto", "topic", "comments"],
        )

        self.ff1.showFields = ("topic", "comments")
        self.assertEqual(
            list(filter_widgets(self.ff1, self.dummy_form.w).keys()),
            ["replyto", "topic", "comments"],
        )

        self.ff1.showAll = False
        self.assertEqual(
            list(filter_widgets(self.ff1, self.dummy_form.w).keys()),
            ["topic", "comments"],
        )

    def test_selective_fields(self):
        """ Test selective inclusion of fields for mail and thank you page.

        This uses filter_fields, which needs as input:
        - a context (the form or a mailer)
        - a list of widgets
        - (unsorted) data (user input from the request)
        - optional omit=True/False (default False)

        With omit=True, we get a list of field names to omit.
        With omit=False, we get an ordered dict of fields to include.
        """
        # Test the types of answers.
        from collections import OrderedDict as BaseDict
        from collective.easyform.api import OrderedDict

        self.assertIsInstance(
            filter_fields(self.ff1, self.dummy_form.schema, {}), OrderedDict
        )
        self.assertIsInstance(
            filter_fields(self.ff1, self.dummy_form.schema, {}), BaseDict
        )
        self.assertIsInstance(filter_fields(self.ff1, self.dummy_form.schema, {}), dict)
        self.assertIsInstance(
            filter_fields(self.ff1, self.dummy_form.schema, {}, omit=True), list
        )

        # Empty data
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, {}).keys()), [],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, {}, omit=True)), [],
        )

        # All data empty
        data = {"replyto": "", "topic": "", "comments": ""}
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).keys()),
            ["replyto", "topic", "comments"],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).values()),
            ["", "", ""],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data, omit=True)), [],
        )
        self.ff1.includeEmpties = False
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).keys()), [],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data, omit=True)),
            ["replyto", "topic", "comments"],
        )

        # All data filled in
        data = {"replyto": "me@example.org", "topic": "Test", "comments": "Ni"}
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).keys()),
            ["replyto", "topic", "comments"],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).values()),
            ["me@example.org", "Test", "Ni"],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data, omit=True)), [],
        )

        # Show only specific fields, not active when showAll=True.
        self.ff1.showFields = ("no-such-field", "topic", "comments")
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).keys()),
            ["replyto", "topic", "comments"],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data, omit=True)), [],
        )

        # Only show specific fields.
        self.ff1.showAll = False
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).keys()),
            ["topic", "comments"],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data, omit=True)),
            ["replyto"],
        )

        # The order of showFields is kept.
        # Note: currently the order is used on the mail template,
        # but not on the thanks page.
        self.ff1.showFields = ("comments", "no-such-field", "topic")
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data).keys()),
            ["comments", "topic"],
        )
        self.assertEqual(
            list(filter_fields(self.ff1, self.dummy_form.schema, data, omit=True)),
            ["replyto"],
        )
