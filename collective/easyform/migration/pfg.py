# -*- coding: utf-8 -*-
from collections import namedtuple
from collective.easyform.migration.actions import actions_model
from collective.easyform.migration.data import SavedDataMigrator
from collective.easyform.migration.fields import fields_model
from plone.app.contenttypes.migration.field_migrators import (
    migrate_richtextfield,  # noqa
)
from plone.app.contenttypes.migration.field_migrators import migrate_simplefield  # noqa
from plone.app.contenttypes.migration.migration import ATCTContentMigrator
from plone.app.contenttypes.migration.migration import migrate
from plone.autoform.form import AutoExtensibleForm
from plone.protect.interfaces import IDisableCSRFProtection
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from six import StringIO
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from zope import schema
from zope.component.hooks import getSite
from zope.interface import alsoProvides


import logging
import transaction


logger = logging.getLogger("collective.easyform.migration")

Field = namedtuple("Type", ["name", "handler"])

FIELD_MAPPING = {
    "submitLabel": Field("submitLabel", migrate_simplefield),
    "resetLabel": Field("resetLabel", migrate_simplefield),
    "useCancelButton": Field("useCancelButton", migrate_simplefield),
    "forceSSL": Field("forceSSL", migrate_simplefield),
    "formPrologue": Field("formPrologue", migrate_richtextfield),
    "formEpilogue": Field("formEpilogue", migrate_richtextfield),
    "thanksPageOverride": Field("thanksPageOverride", migrate_simplefield),
    "formActionOverride": Field("formActionOverride", migrate_simplefield),
    "onDisplayOverride": Field("onDisplayOverride", migrate_simplefield),
    "afterValidationOverride": Field(
        "afterValidationOverride", migrate_simplefield
    ),  # noqa
    "headerInjection": Field("headerInjection", migrate_simplefield),
    "checkAuthenticator": Field("CSRFProtection", migrate_simplefield),
}


class PloneFormGenMigrator(ATCTContentMigrator):
    """Migrator for PFG to easyform"""

    src_portal_type = "FormFolder"
    src_meta_type = "FormFolder"
    dst_portal_type = "EasyForm"
    dst_meta_type = None  # not used
    saved_data_migrator = SavedDataMigrator()

    def migrate_ploneformgen(self):
        for pfg_field, ef_field in FIELD_MAPPING.items():
            ef_field.handler(self.old, self.new, pfg_field, ef_field.name)
        self.new.fields_model = fields_model(self.old)
        self.new.actions_model = actions_model(self.old)

        self.migrate_thankyou_page()

        self.saved_data_migrator.migrate(self.old, self.new)

    def migrate(self, unittest=0):
        super(PloneFormGenMigrator, self).migrate()
        logger.info("Migrated FormFolder %s", "/".join(self.new.getPhysicalPath()))

    def migrate_thankyou_page(self):
        pfg_thankspage = self.old.get(self.old.getThanksPage())
        if pfg_thankspage:
            ef = self.new

            ef.thankstitle = pfg_thankspage.title
            ef.thanksdescription = pfg_thankspage.Description()
            ef.showAll = pfg_thankspage.showAll
            ef.showFields = pfg_thankspage.showFields
            ef.includeEmpties = pfg_thankspage.includeEmpties
            Field("thanksPrologue", migrate_richtextfield).handler(
                pfg_thankspage, ef, "thanksPrologue", "thanksPrologue"
            )
            Field("thanksEpilogue", migrate_richtextfield).handler(
                pfg_thankspage, ef, "thanksEpilogue", "thanksEpilogue"
            )

class IMigratePloneFormGenFormSchema(model.Schema):
    dry_run = schema.Bool(
        title=u"Dry run",
        required=True,
        default=False,
    )


class MigratePloneFormGenForm(AutoExtensibleForm, Form):
    label = u"Migrate PloneFormGen Forms"
    ignoreContext = True
    schema = IMigratePloneFormGenFormSchema
    migrator = PloneFormGenMigrator

    @buttonAndHandler(u"Migrate")
    def handle_migrate(self, action):
        data, errors = self.extractData()
        if len(errors) > 0:
            return

        self.log = StringIO()
        handler = logging.StreamHandler(self.log)
        logger.addHandler(handler)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)

        self.migrate()

        self.migration_done = True
        if data.get("dry_run", False):
            transaction.abort()
            logger.info(u"PloneFormGen migration finished (dry run)")
        else:
            logger.info(u"PloneFormGen migration finished")

    def migrate(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = getSite()

        # Switch linkintegrity off temporarily.
        ptool = getToolByName(self.context, "portal_properties")
        site_props = getattr(ptool, "site_properties", None)
        link_integrity = False
        if site_props and site_props.hasProperty("enable_link_integrity_checks"):
            link_integrity = site_props.getProperty(
                "enable_link_integrity_checks", False
            )
            if link_integrity:
                site_props.manage_changeProperties(enable_link_integrity_checks=False)
        migrate(portal, self.migrator)

        # Switch linkintegrity back on, if needed
        if link_integrity:
            site_props.manage_changeProperties(enable_link_integrity_checks=True)

    def render(self):
        if getattr(self, "migration_done", False):
            return self.log.getvalue()
        return super(MigratePloneFormGenForm, self).render()
