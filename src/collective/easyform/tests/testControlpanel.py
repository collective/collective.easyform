# -*- coding: utf-8 -*-
from collective.easyform.tests import base
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


try:
    from plone.testing.zope import Browser
except ImportError:
    from plone.testing.z2 import Browser


class ControlPanelTestCase(base.EasyFormTestCase):
    """Test that changes in the easyform control panel are actually
    stored in the registry.
    """

    def setUp(self):
        self.portal_url = self.layer["portal"].absolute_url()
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic " + SITE_OWNER_NAME + ":" + SITE_OWNER_PASSWORD
        )

    def test_easyform_control_panel_link_to_overview(self):
        self.browser.open(self.portal_url + "/@@overview-controlpanel")
        link = self.browser.getLink("easyform")
        self.assertEqual(link.url, "http://nohost/plone/@@easyform-controlpanel")

    def test_easyform_control_panel_contents(self):
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        self.assertTrue("easyform Settings" in self.browser.contents)
        self.assertTrue("Allowed Fields" in self.browser.contents)
        self.assertTrue("CSV delimiter" in self.browser.contents)
        input = self.browser.getControl(label="CSV delimiter")
        self.assertEqual(input.value, ",")

    def test_easyform_control_panel_sidebar(self):
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        self.assertTrue("General" in self.browser.contents)
        link = self.browser.getLink("Add-ons")
        self.assertEqual(link.url, "http://nohost/plone/prefs_install_products_form")


class ControlPanelFunctionalTestCase(base.EasyFormFunctionalTestCase):
    """Test that changes in the easyform control panel are actually
    stored in the registry.
    """

    def setUp(self):
        self.portal_url = self.layer["portal"].absolute_url()
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic " + SITE_OWNER_NAME + ":" + SITE_OWNER_PASSWORD
        )

    def test_easyform_control_panel_allowed_fields_saved(self):
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        self.browser.getControl("Rich Text").selected = False
        self.browser.getControl("Save").click()
        registry = getUtility(IRegistry)
        self.assertNotIn(
            "plone.app.textfield.RichText",
            registry.records["easyform.allowedFields"].value,
        )

    def test_easyform_control_panel_CSV_delimiter_saved(self):
        registry = getUtility(IRegistry)
        self.assertEqual(
            registry.records["easyform.csv_delimiter"].value,
            ",",
        )
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        input = self.browser.getControl(label="CSV delimiter")
        input.value = ";"
        self.browser.getControl("Save").click()
        self.assertEqual(
            registry.records["easyform.csv_delimiter"].value,
            ";",
        )

    def test_easyform_control_panel_CSV_delimiter_limited_to_one_char(self):
        registry = getUtility(IRegistry)
        self.assertEqual(
            registry.records["easyform.csv_delimiter"].value,
            ",",
        )
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        input = self.browser.getControl(label="CSV delimiter")
        input.value = "comma"
        self.browser.getControl("Save").click()
        self.assertTrue("Value is too long" in self.browser.contents)
        self.assertEqual(
            registry.records["easyform.csv_delimiter"].value,
            ",",
        )

    def test_easyform_control_panel_CSV_delimiter_required(self):
        registry = getUtility(IRegistry)
        self.assertEqual(
            registry.records["easyform.csv_delimiter"].value,
            ",",
        )
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        input = self.browser.getControl(label="CSV delimiter")
        input.value = ""
        self.browser.getControl("Save").click()
        self.assertTrue("Required input is missing." in self.browser.contents)
        input = self.browser.getControl(label="CSV delimiter")
        self.assertEqual(input.value, "")
        self.assertEqual(
            registry.records["easyform.csv_delimiter"].value,
            ",",
        )


# EOF
