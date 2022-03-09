# -*- coding: utf-8 -*-
from ast import literal_eval
from collective.easyform.api import get_actions
from collective.easyform.api import get_fields
from collective.easyform.interfaces import ISaveData
import DateTime
from plone.namedfile.interfaces import INamedBlobFileField
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
            for idx, row in enumerate(data_adapter.getSavedFormInput()):
                if len(row) != len(cols):
                    logger.warning(
                        "Number of columns does not match. Skipping row %s in "
                        "data adapter %s/%s",
                        idx,
                        "/".join(easyform.getPhysicalPath()),
                        data_adapter.getId(),
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
                    ):
                        # Exceptions above are often due to long living Forms, where users have changed their minds about
                        # the Field formats/widgets...
                        # Older datarows can break in these cases
                        logger.exception(
                            "Error for {}:'{}' in the {}/{} data adapter. Value was skipped during migration".format(
                                key,
                                value,
                                "/".join(easyform.getPhysicalPath()),
                                data_adapter.getId(),
                            )
                        )
                        continue
                    data[key] = value
                action.addDataRow(data)
