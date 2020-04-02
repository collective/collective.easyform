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


class AllowedFieldsControlPanelFuncionalTest(base.EasyFormTestCase):
    """Test that changes in the easyform control panel are actually
    stored in the registry.
    """

    def setUpPloneSite(self):
        pass

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic " + SITE_OWNER_NAME + ":" + SITE_OWNER_PASSWORD
        )

    def test_easyform_control_panel_link(self):
        self.browser.open(self.portal_url + "/@@overview-controlpanel")
        self.browser.getLink("easyform").click()
        self.assertTrue("easyform Settings" in self.browser.contents)

    def test_easyform_control_panel_backlink(self):
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        self.assertTrue("General" in self.browser.contents)

    def test_easyform_control_panel_sidebar(self):
        self.browser.open(self.portal_url + "/@@navigation-controlpanel")
        self.browser.getLink("Site Setup").click()
        self.assertEqual(
            self.browser.url, "http://nohost/plone/@@overview-controlpanel"
        )

    def test_easyform_control_panel_checkbox(self):
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        self.browser.getControl("Rich Text").selected = False
        self.browser.getControl("Save").click()
        registry = getUtility(IRegistry)
        self.assertNotIn(
            "plone.app.textfield.RichText",
            registry.records["easyform.allowedFields"].value,
        )


# EOF
