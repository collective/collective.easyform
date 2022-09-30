# -*- coding: utf-8 -*-
from ast import literal_eval
from collective.easyform.api import get_actions
from collective.easyform.api import get_fields
from collective.easyform.interfaces import ISaveData
import DateTime
from plone.namedfile.interfaces import INamedBlobFileField
from Products.CMFPlone.utils import safe_unicode
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ISet
from zope.schema.interfaces import ValidationError
import logging

logger = logging.getLogger("collective.easyform.migration")

class ConversionError(ValueError):
    pass


def convert_value(key, value, easyform):
    schema = get_fields(easyform)
    try:
        field = schema.get(key)
        value = value.decode("utf8")
        if IFromUnicode.providedBy(field) and value:
            value = field.fromUnicode(value)
        elif IDatetime.providedBy(field) and value:
            value = DateTime.DateTime(value).asdatetime()
        elif IDate.providedBy(field) and value:
            value = DateTime.DateTime(value).asdatetime().date()
        elif ISet.providedBy(field):
            value = set(literal_eval(value))
        elif INamedBlobFileField.providedBy(field):
            value = None
        return value
    except (
        ValueError,
        TypeError,
        ValidationError,
        SyntaxError,
        DateTime.interfaces.SyntaxError,
        DateTime.interfaces.TimeError,
        DateTime.interfaces.DateError
    ):
        # Exceptions above are often due to long living Forms, where users have changed their minds about
        # the Field formats/widgets...
        # Older datarows can break in these cases

        try:
            value_to_log = safe_unicode(value)
        except UnicodeError:
            # in case of file field, try to log the file name
            # which is seperated with a colon
            if ':' in value:
                value_to_log = safe_unicode(value.split(':')[0])
            else:
                # xxx we hope we are lucky that there are no broken characters in the first 50
                value_to_log = safe_unicode(value)[:50]

        logger.exception(
            u"Error for {}:'{}' in the {} data adapter.".format(
                key,
                value_to_log,
                "/".join(easyform.getPhysicalPath())
            )
        )
        raise ConversionError()


class SavedDataMigrator(object):

    def should_migrate_row(self, data_adapter, easyform, row, idx):
        cols = data_adapter.getColumnNames()
        if len(row) == len(cols):
            return True
        else:
            logger.info(
                "Column count mismatch at row %s",
                idx,
            )
            return False

    def migrate_row(self, data_adapter, easyform, row):
        cols = data_adapter.getColumnNames()
        data = {}
        for key, value in zip(cols, row):
            value = convert_value(key, value, easyform)
            data[key] = value
        return data

    def migrate(self, ploneformgen, easyform):
        for data_adapter in ploneformgen.objectValues("FormSaveDataAdapter"):
            actions = get_actions(easyform)
            action = actions.get(data_adapter.getId())
            if ISaveData.providedBy(action):
                has_failed_row = False
                for idx, row in enumerate(data_adapter.getSavedFormInput()):
                    if not self.should_migrate_row(data_adapter, easyform, row, idx):
                        if not has_failed_row:
                            logger.warning(
                                "Some data were skipped in "
                                "data adapter %s/%s.\n Use loglevel INFO for more details.",
                                "/".join(easyform.getPhysicalPath()),
                                data_adapter.getId(),
                            )
                        has_failed_row = True
                        continue
                    try:
                        data = self.migrate_row(data_adapter, easyform, row)
                        action.addDataRow(data)
                    except ConversionError:
                        logger.warning(
                            "BEWARE: to keep data integrity, the data was not migrated for "
                            "data adapter %s/%s.",
                            "/".join(easyform.getPhysicalPath()),
                            data_adapter.getId(),
                        )
                        action.clearSavedFormInput()
                        return

