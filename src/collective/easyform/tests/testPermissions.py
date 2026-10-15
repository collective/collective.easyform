#
# Test EasyForm permissions.
#

from AccessControl.unauthorized import Unauthorized
from collective.easyform.tests import base
from plone import api


class TestPermissions(base.EasyFormTestCase):
    """Ensure the rolemap grants the intended roles"""

    # Roles which are granted each permission on the site root.
    EXPECTED_ROLES = {
        "collective.easyform: Add Content": (
            "Contributor",
            "Manager",
            "Owner",
            "Site Administrator",
        ),
        "collective.easyform: Add Mailers": (
            "Editor",
            "Manager",
            "Owner",
            "Site Administrator",
        ),
        "collective.easyform: Add Data Savers": (
            "Editor",
            "Manager",
            "Owner",
            "Site Administrator",
        ),
        "collective.easyform: Edit Advanced Fields": (
            "Editor",
            "Manager",
            "Owner",
            "Site Administrator",
        ),
        "collective.easyform: Edit Mail Addresses": (
            "Editor",
            "Manager",
            "Owner",
            "Site Administrator",
        ),
        "collective.easyform: Download Saved Input": (
            "Manager",
            "Owner",
            "Reviewer",
            "Site Administrator",
        ),
    }

    EDITOR_PERMISSIONS = (
        "collective.easyform: Add Mailers",
        "collective.easyform: Add Data Savers",
        "collective.easyform: Edit Advanced Fields",
        "collective.easyform: Edit Mail Addresses",
    )

    def afterSetUp(self):
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = self.folder.ff1
        api.user.create(email="user@example.org", username="user")

    def roles_of_permission(self, permission):
        return sorted(
            role["name"]
            for role in self.portal.rolesOfPermission(permission)
            if role["selected"]
        )

    def test_add_permissions(self):
        """Test to make sure add permissions are as intended"""
        fti = self.portal.portal_types["EasyForm"]
        self.assertEqual(fti.add_permission, "collective.easyform.AddContent")

    def test_rolemap(self):
        for permission, roles in self.EXPECTED_ROLES.items():
            self.assertEqual(
                self.roles_of_permission(permission), sorted(roles), permission
            )

    def test_editor_permissions(self):
        api.user.grant_roles(username="user", obj=self.ff1, roles=["Editor"])
        for permission in self.EDITOR_PERMISSIONS:
            self.assertTrue(
                api.user.has_permission(permission, username="user", obj=self.ff1),
                permission,
            )
        # Editors may not download saved data.
        self.assertFalse(
            api.user.has_permission(
                "collective.easyform: Download Saved Input",
                username="user",
                obj=self.ff1,
            )
        )

    def test_reviewer_permissions(self):
        api.user.grant_roles(username="user", obj=self.ff1, roles=["Reviewer"])
        self.assertTrue(
            api.user.has_permission(
                "collective.easyform: Download Saved Input",
                username="user",
                obj=self.ff1,
            )
        )
        # Reviewers may not edit the form.
        for permission in self.EDITOR_PERMISSIONS:
            self.assertFalse(
                api.user.has_permission(permission, username="user", obj=self.ff1),
                permission,
            )

    def test_owner_can_access_saveddata_view(self):
        api.user.grant_roles(username="user", obj=self.ff1, roles=["Owner"])
        with api.env.adopt_user(username="user"):
            self.assertIsNotNone(self.ff1.restrictedTraverse("saveddata"))

    def test_reviewer_can_access_saveddata_view(self):
        api.user.grant_roles(username="user", obj=self.ff1, roles=["Reviewer"])
        with api.env.adopt_user(username="user"):
            self.assertIsNotNone(self.ff1.restrictedTraverse("saveddata"))

    def test_non_reviewer_cannot_access_saveddata_view(self):
        # Without Reviewer (or Owner/Manager), saved data may not be downloaded.
        api.user.grant_roles(
            username="user", obj=self.ff1, roles=["Reader", "Contributor", "Editor"]
        )
        self.assertFalse(
            api.user.has_permission(
                "collective.easyform: Download Saved Input",
                username="user",
                obj=self.ff1,
            )
        )
        with api.env.adopt_user(username="user"):
            with self.assertRaises(Unauthorized):
                self.ff1.restrictedTraverse("saveddata")

    def test_upgrade_1018(self):
        # Simulate the state before the upgrade.
        for permission, roles in self.EXPECTED_ROLES.items():
            old_roles = [r for r in roles if r not in ("Editor", "Reviewer")]
            self.portal.manage_permission(permission, roles=old_roles, acquire=True)
        self.assertNotIn(
            "Editor", self.roles_of_permission("collective.easyform: Add Mailers")
        )
        self.assertNotIn(
            "Reviewer",
            self.roles_of_permission("collective.easyform: Download Saved Input"),
        )

        portal_setup = self.portal.portal_setup
        profile_id = "profile-collective.easyform:default"
        portal_setup.setLastVersionForProfile(profile_id, "1017")
        portal_setup.upgradeProfile(profile_id, dest="1018")

        for permission, roles in self.EXPECTED_ROLES.items():
            self.assertEqual(
                self.roles_of_permission(permission), sorted(roles), permission
            )
