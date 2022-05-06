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
            recaptcha_in_form = [
                "Recaptcha found"
                for tuple in schema.namesAndDescriptions()
                if "ReCaptcha" in tuple[1].__str__()
            ]
            for idx, row in enumerate(data_adapter.getSavedFormInput()):
                if len(row) != len(cols):
                    import pdb

                    pdb.set_trace()
                    if not (
                        len(cols) - len(row) == 1
                        and recaptcha_in_form
                        and "x" not in row
                    ):
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
                        logger.exception(
                            u"Error for {}:'{}' in the {}/{} data adapter.".format(
                                key,
                                safe_unicode(value)[:50],
                                "/".join(easyform.getPhysicalPath()),
                                data_adapter.getId(),
                            )
                        )
                        logger.warning(
                            "To Keep data entigrity, the data was not migrated for "
                            "data adapter %s/%s",
                            "/".join(easyform.getPhysicalPath()),
                            data_adapter.getId(),
                        )
                        action.clearSavedFormInput()
                        return
                    data[key] = value
                action.addDataRow(data)
