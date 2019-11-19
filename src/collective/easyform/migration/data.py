# -*- coding: utf-8 -*-
from ast import literal_eval
from collective.easyform.api import get_actions
from collective.easyform.api import get_schema
from collective.easyform.interfaces import ISaveData
from DateTime import DateTime
from plone.namedfile.interfaces import INamedBlobFileField
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ISet

import logging

logger = logging.getLogger('collective.easyform.migration')


def migrate_saved_data(ploneformgen, easyform):
    for data_adapter in ploneformgen.objectValues('FormSaveDataAdapter'):
        actions = get_actions(easyform)
        action = actions.get(data_adapter.getId())
        schema = get_schema(easyform)
        if ISaveData.providedBy(action):
            cols = data_adapter.getColumnNames()
            for idx, row in enumerate(data_adapter.getSavedFormInput()):
                if len(row) != len(cols):
                    logger.warning(
                        'Number of columns does not match. Skipping row %s in '
                        'data adapter %s/%s', idx,
                        '/'.join(easyform.getPhysicalPath()),
                        data_adapter.getId())
                    continue
                data = {}
                for key, value in zip(cols, row):
                    field = schema.get(key)
                    value = value.decode('utf8')
                    if IFromUnicode.providedBy(field):
                        value = field.fromUnicode(value)
                    elif IDatetime.providedBy(field) and value:
                        value = DateTime(value).asdatetime()
                    elif IDate.providedBy(field) and value:
                        value = DateTime(value).asdatetime().date()
                    elif ISet.providedBy(field):
                        try:
                            value = set(literal_eval(value))
                        except ValueError:
                            pass
                    elif INamedBlobFileField.providedBy(field):
                        value = None
                    data[key] = value
                action.addDataRow(data)
