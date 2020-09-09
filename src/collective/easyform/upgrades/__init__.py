from plone import api

import logging


logger = logging.getLogger(__name__)


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
    logger.info("Updated the last_compilation date of the easyform bundle.")

    # Run the combine-bundles import step or its handler.
    # Can be done with an upgrade step:
    #   <gs:upgradeDepends
    #     title="combine bundles"
    #     import_steps="combine-bundles"
    #     run_deps="false"
    #     />
    # But directly calling the basic function works fine.
    # See also comment here:
    # https://github.com/collective/collective.easyform/pull/248#issuecomment-689365240
    # Also, here we can do a try/except so it does not fail on Plone 5.0,
    # which I think does not have the import step, not the function.
    try:
        from Products.CMFPlone.resources.browser.combine import combine_bundles
    except ImportError:
        logger.warning("Could not call combine_bundles. You should do that yourself.")
        return
    portal = api.portal.get()
    combine_bundles(portal)
