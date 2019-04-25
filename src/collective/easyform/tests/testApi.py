# -*- coding: utf-8 -*-
#
# Integeration tests specific to the mailer
#

from collective.easyform.actions import DummyFormView
from collective.easyform.api import filter_widgets
from collective.easyform.api import get_schema
from collective.easyform.tests import base


class TestFunctions(base.EasyFormTestCase):
    """ Test mailer action """

    def afterSetUp(self):
        super(TestFunctions, self).afterSetUp()
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.dummy_form = DummyFormView(self.ff1, self.layer["request"])
        self.dummy_form.schema = get_schema(self.ff1)
        self.dummy_form.prefix = "form"
        self.dummy_form._update()

    def test_selective_widgets(self):
        """ Test selective inclusion of widgets for mail and thank you page """

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
