# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and installer."""
        return ["collective.easyform:uninstall"]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and installer.

        Our upgrades profiles are defined in the directory 'upgrades'.
        Plone sees this as a separate product.
        So instead of adding each new upgrade profile to the list of
        non installable profiles above, we can mark the upgrades product
        as non installable.
        """
        return ["collective.easyform.upgrades"]
