def update_last_compilation(context):
    # Let's do the imports inline, so they are not needlessly done at startup.
    # Should not really matter, but oh well.
    from datetime import datetime
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
    from Products.CMFPlone.interfaces import IBundleRegistry

    registry = getUtility(IRegistry)
    records = registry.forInterface(IBundleRegistry, prefix="plone.bundles/easyform")
    # Technically we only need year, month and day.
    # But keep this in sync with registry.xml.
    records.last_compilation = datetime(2020, 9, 8, 17, 52, 0)
    # TODO: run the combine-bundles import step or its handler
    # Products.CMFPlone.resources.exportimport.bundles.combine.
    # But that only does something when there is a registry.xml,
    # so I don't think it works for an upgrade step.
    #
    # But this is a wrapper around
    # Products.CMFPlone.resources.browser.combine.combine_bundles
    # which we could call directly, but then we need to do the same
    # extra handling of the response contenttype.
    #
    # We could also re-apply our whole registry.xml,
    # by doing an upgradeDepends with plone.app.registry and combine-bundles,
    # but that restores our factory defaults, which we should not do.
    #
    # Easiest is to add an upgrade profile.
    # I always consider that overkill, but so be it.
