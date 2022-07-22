from plone import api

import logging


logger = logging.getLogger(__name__)


def update_last_compilation(context, timetuple=None):
    # Let's do the imports inline, so they are not needlessly done at startup.
    # Should not really matter, but oh well.
    from datetime import datetime
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces import IBundleRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    records = registry.forInterface(IBundleRegistry, prefix="plone.bundles/easyform")
    # Technically we only need year, month and day.
    # But keep this in sync with registry.xml.
    records.last_compilation = datetime(*timetuple)
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


def update_last_compilation_1007(context):
    update_last_compilation(context, (2020, 9, 8, 14, 2, 0))


def update_last_compilation_1008(context):
    update_last_compilation(context, (2020, 12, 9, 14, 2, 0))


def update_last_compilation_1009(context):
    update_last_compilation(context, (2021, 8, 31, 0, 0, 0))


def fix_savedata_persistence_issues(context):

    from persistent.mapping import PersistentMapping

    catalog = api.portal.get_tool("portal_catalog")
    forms = catalog.unrestrictedSearchResults(portal_type='EasyForm')
    for item in forms:
        form = item.getObject()
        if hasattr(form, '_inputStorage'):
            # Convert to persistent mapping
            form._inputStorage = PersistentMapping(form._inputStorage)
            logger.info(
                'Fixed storage of {}'.format('/'.join(form.getPhysicalPath()))
            )


def change_saveddata_action_permission(context):
    portal_actions = api.portal.get_tool("portal_actions")
    category = portal_actions.get("object_buttons")
    if category is None:
        return
    action = category.get("saveddata")
    if action is None:
        return
    action._setPropValue('permissions', ("collective.easyform: Download Saved Input",))


def remove_migrate_all_forms_record(context):
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    record = "easyform.migrate_all_forms"
    if record in registry.records:
        del registry.records[record]
        logger.info("Removed {} registry record".format(record))
