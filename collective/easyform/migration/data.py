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

def should_migrate_row(data_adapter, easyform, idx, row, has_failed_row):
    cols = data_adapter.getColumnNames()
    if len(row) != len(cols):
        if not has_failed_row:
            logger.warning(
                "Number of columns does not match for all rows. Some data were skipped in "
                "data adapter %s/%s",
                "/".join(easyform.getPhysicalPath()),
                data_adapter.getId(),
            )
        logger.info(
            "Column count mismatch at row %s",
            idx,
        )
        return False
    else:
        return True

def migrate_saved_data(ploneformgen, easyform):
    for data_adapter in ploneformgen.objectValues("FormSaveDataAdapter"):
        actions = get_actions(easyform)
        action = actions.get(data_adapter.getId())
        schema = get_fields(easyform)
        if ISaveData.providedBy(action):
            cols = data_adapter.getColumnNames()
            has_failed_row = False
            for idx, row in enumerate(data_adapter.getSavedFormInput()):
                if not should_migrate_row(data_adapter, easyform, idx, row, has_failed_row):
                    has_failed_row = True
                    continue

                data = {}
                for key, value in zip(cols, row):
                    try:
                        field = schema.get(key)
                        value = safe_unicode(value)
                        if IFromUnicode.providedBy(field) and value:
                            value = field.fromUnicode(value)
                        elif IDatetime.providedBy(field) and value:
                            value = DateTime.DateTime(value).asdatetime()
                        elif IDate.providedBy(field) and value:
                            value = DateTime.DateTime(value).asdatetime().date()
                        elif ISet.providedBy(field):
                            if not value or value == [""]:
                                value = set()
                            else:
                                value = set(value)
                        elif INamedBlobFileField.providedBy(field):
                            value = None
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
                            u"Error for {}:'{}' in the {}/{} data adapter.".format(
                                key,
                                value_to_log,
                                "/".join(easyform.getPhysicalPath()),
                                data_adapter.getId(),
                            )
                        )
                        logger.warning(
                            "BEWARE: to keep data integrity, the data was not migrated for "
                            "data adapter %s/%s.",
                            "/".join(easyform.getPhysicalPath()),
                            data_adapter.getId(),
                        )
                        action.clearSavedFormInput()
                        return
                    data[key] = value
                action.addDataRow(data)
