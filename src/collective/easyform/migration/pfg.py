# -*- coding: utf-8 -*-
from collections import namedtuple
from collective.easyform.migration.actions import actions_model
from collective.easyform.migration.data import migrate_saved_data
from collective.easyform.migration.fields import fields_model
from plone import api
from plone.app.contenttypes.migration.field_migrators import migrate_richtextfield  # noqa
from plone.app.contenttypes.migration.field_migrators import migrate_simplefield  # noqa
from plone.app.contenttypes.migration.migration import ATCTContentMigrator
from plone.app.contenttypes.migration.migration import migrate
from plone.autoform.form import AutoExtensibleForm
from plone.protect.interfaces import IDisableCSRFProtection
from plone.supermodel import model
from six import StringIO
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from zope import schema
from zope.interface import alsoProvides
import logging
import transaction


logger = logging.getLogger('collective.easyform.migration')

Field = namedtuple('Type', ['name', 'handler'])

FIELD_MAPPING = {
    'submitLabel': Field('submitLabel', migrate_simplefield),
    'resetLabel': Field('resetLabel', migrate_simplefield),
    'useCancelButton': Field('useCancelButton', migrate_simplefield),
    'forceSSL': Field('forceSSL', migrate_simplefield),
    'formPrologue': Field('formPrologue', migrate_richtextfield),
    'formEpilogue': Field('formEpilogue', migrate_richtextfield),
    'thanksPageOverride': Field('thanksPageOverride', migrate_simplefield),
    'formActionOverride': Field('formActionOverride', migrate_simplefield),
    'onDisplayOverride': Field('onDisplayOverride', migrate_simplefield),
    'afterValidationOverride': Field('afterValidationOverride', migrate_simplefield),  # noqa
    'headerInjection': Field('headerInjection', migrate_simplefield),
    'checkAuthenticator': Field('CSRFProtection', migrate_simplefield),
}


class PloneFormGenMigrator(ATCTContentMigrator):
    """Migrator for PFG to easyform"""

    src_portal_type = 'FormFolder'
    src_meta_type = 'FormFolder'
    dst_portal_type = 'EasyForm'
    dst_meta_type = None  # not used

    def migrate_ploneformgen(self):
        for pfg_field, ef_field in FIELD_MAPPING.items():
            ef_field.handler(self.old, self.new, pfg_field, ef_field.name)
        self.new.fields_model = fields_model(self.old)
        self.new.actions_model = actions_model(self.old)

        migrate_saved_data(self.old, self.new)

    def migrate(self, unittest=0):
        super(PloneFormGenMigrator, self).migrate()
        logger.info(
            'Migrated FormFolder %s',
            '/'.join(self.new.getPhysicalPath()))


class IMigratePloneFormGenFormSchema(model.Schema):
    dry_run = schema.Bool(
        title=u'Dry run',
        required=True,
        default=False,
    )


class MigratePloneFormGenForm(AutoExtensibleForm, Form):
    label = u'Migrate PloneFormGen Forms'
    ignoreContext = True
    schema = IMigratePloneFormGenFormSchema

    @buttonAndHandler(u'Migrate')
    def handle_migrate(self, action):
        data, errors = self.extractData()
        if len(errors) > 0:
            return

        self.log = StringIO()
        handler = logging.StreamHandler(self.log)
        logger.addHandler(handler)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s')
        handler.setFormatter(formatter)

        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        migrate(portal, PloneFormGenMigrator)

        self.migration_done = True
        if data.get('dry_run', False):
            transaction.abort()
            logger.info(u'PloneFormGen migration finished (dry run)')
        else:
            logger.info(u'PloneFormGen migration finished')

    def render(self):
        if getattr(self, 'migration_done', False):
            return self.log.getvalue()
        return super(MigratePloneFormGenForm, self).render()
