# -*- coding: utf-8 -*-
#
# Test EasyForm initialisation and set-up
#

from collective.easyform.tests import base
from plone import api
from Products.CMFCore.utils import getToolByName

import Products


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    # BBB for Plone 5.0 and lower.
    get_installer = None


def getAddPermission(product, name):
    """find the add permission for a meta_type"""

    name = "{0}: {1}".format(product, name)
    for mt in Products.meta_types:
        if mt["name"] == name:
            return mt["permission"]
    return ""


class TestInstallation(base.EasyFormTestCase):

    """Ensure product is properly installed"""

    def afterSetUp(self):
        base.EasyFormTestCase.afterSetUp(self)

        self.types = self.portal.portal_types
        self.controlpanel = self.portal.portal_controlpanel

        self.metaTypes = ("EasyForm",)

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.assertTrue(t in self.types.objectIds())

    def testTypeActions(self):
        # hide properties/references tabs
        for typ in self.metaTypes:
            for act in self.types[typ].listActions():
                if act.id in ["metadata", "references"]:
                    self.assertFalse(act.visible)
                if act.id in ["actions", "fields"]:
                    self.assertTrue(act.visible)

    def testArchetypesToolCatalogRegistration(self):
        at_tool = getToolByName(self.portal, "archetype_tool", None)
        if not at_tool:
            return
        for t in self.metaTypes:
            self.assertEqual(1, len(at_tool.getCatalogsByType(t)))
            self.assertEqual("portal_catalog", at_tool.getCatalogsByType(t)[0].getId())

    def ttestControlPanelConfigletInstalled(self):
        self.assertTrue(
            "EasyForm" in [action.id for action in self.controlpanel.listActions()]
        )

    def ttestAddPermissions(self):
        """Test to make sure add permissions are as intended"""

        ADD_CONTENT_PERMISSION = "EasyForm: Add Content"
        CSA_ADD_CONTENT_PERMISSION = "EasyForm: Add Custom Scripts"
        MA_ADD_CONTENT_PERMISSION = "EasyForm: Add Mailers"
        SDA_ADD_CONTENT_PERMISSION = "EasyForm: Add Data Savers"

        self.assertEqual(
            getAddPermission("EasyForm", "EasyForm"), ADD_CONTENT_PERMISSION
        )
        self.assertEqual(
            getAddPermission("EasyForm", "Mailer Adapter"), MA_ADD_CONTENT_PERMISSION
        )
        self.assertEqual(
            getAddPermission("EasyForm", "Save Data Adapter"),
            SDA_ADD_CONTENT_PERMISSION,
        )
        self.assertEqual(
            getAddPermission("EasyForm", "Custom Script Adapter"),
            CSA_ADD_CONTENT_PERMISSION,
        )

    def testActionsInstalled(self):
        self.assertTrue(
            self.portal.portal_actions.getActionInfo("object_buttons/export")
        )
        self.assertTrue(
            self.portal.portal_actions.getActionInfo("object_buttons/import")
        )
        self.assertTrue(
            self.portal.portal_actions.getActionInfo("object_buttons/saveddata")
        )

    def test_EasyFormInDefaultPageTypes(self):
        values = api.portal.get_registry_record("plone.default_page_types")
        self.assertIn("EasyForm", values)

    def testTypeViews(self):
        self.assertEqual(
            self.types.EasyForm.getAvailableViewMethods(self.types), ("view",)
        )

    def test_upgrades(self):
        portal_setup = self.portal.portal_setup
        profile_id = "profile-collective.easyform:default"
        self.assertFalse(portal_setup.hasPendingUpgrades())
        portal_setup.setLastVersionForProfile(profile_id, "1000")
        self.assertTrue(portal_setup.hasPendingUpgrades())
        # Biggest test is: do the upgrades run without error?
        portal_setup.upgradeProfile(profile_id)
        self.assertFalse(portal_setup.hasPendingUpgrades())
