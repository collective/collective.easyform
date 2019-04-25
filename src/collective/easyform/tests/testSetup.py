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
    """ find the add permission for a meta_type """

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
        self.properties = self.portal.portal_properties
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
        """ Test to make sure add permissions are as intended """

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

    def testModificationsToPropSheetLinesNotPuged(self):
        property_mappings = [
            {
                "propsheet": "site_properties",
                "added_props": [
                    "use_folder_tabs",
                    "typesLinkToFolderContentsInFC",
                    "default_page_types",
                ],
            }
        ]

        # add garbage prop element to each lines property
        for mapping in property_mappings:
            sheet = self.properties[mapping["propsheet"]]
            for lines_prop in mapping["added_props"]:
                propitems = list(sheet.getProperty(lines_prop))
                propitems.append("foo")
                sheet.manage_changeProperties({lines_prop: propitems})

        # reinstall
        if get_installer is None:
            qi = self.portal["portal_quickinstaller"]
        else:
            qi = get_installer(self.portal)
        qi.reinstallProducts(["collective.easyform"])

        # now make sure our garbage values survived the reinstall
        for mapping in property_mappings:
            sheet = self.properties[mapping["propsheet"]]
            for lines_prop in mapping["added_props"]:
                self.assertTrue(
                    "foo" in sheet.getProperty(lines_prop),
                    "Our garbage item didn't survive reinstall for property "
                    "{0} within property sheet {1}".format(
                        lines_prop, mapping["propsheet"]
                    ),
                )

    def test_EasyFormInDefaultPageTypes(self):
        values = api.portal.get_registry_record("plone.default_page_types")
        self.assertIn("EasyForm", values)

    def testTypeViews(self):
        self.assertEqual(
            self.types.EasyForm.getAvailableViewMethods(self.types), ("view",)
        )
