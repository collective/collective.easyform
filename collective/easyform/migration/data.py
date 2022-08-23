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


def migrate_saved_data(ploneformgen, easyform):
    for data_adapter in ploneformgen.objectValues("FormSaveDataAdapter"):
        actions = get_actions(easyform)
        action = actions.get(data_adapter.getId())
        schema = get_fields(easyform)
        if ISaveData.providedBy(action):
            cols = data_adapter.getColumnNames()
            column_count_mismatch = False
            for idx, row in enumerate(data_adapter.getSavedFormInput()):
                if len(row) != len(cols):
                    if not column_count_mismatch:
                        logger.warning(
                            "Number of columns does not match for all rows. Some data were skipped in "
                            "data adapter %s/%s",
                            "/".join(easyform.getPhysicalPath()),
                            data_adapter.getId(),
                        )
                        column_count_mismatch = True
                    logger.info(
                        "Column count mismatch at row %s",
                        idx,
                    )
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
                            value = set(literal_eval(value))
                        elif INamedBlobFileField.providedBy(field):
                            value = None
                    except (
                        ValueError,
                        TypeError,
                        ValidationError,
                        SyntaxError,
                        DateTime.interfaces.SyntaxError,
                        DateTime.interfaces.TimeError,
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
