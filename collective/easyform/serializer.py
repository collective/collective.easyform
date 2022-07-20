import datetime
from datetime import date, datetime
import imp
import pdb
from dateutil import parser
import json
import logging

from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ISet, IDate, IDatetime

from plone.restapi.serializer.dxcontent import SerializeToJson as DXContentToJson
from plone.restapi.deserializer.dxcontent import (
    DeserializeFromJson as DXContentFromJson,
)
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.interfaces import IRichText

from collective.easyform.api import get_actions
from collective.easyform.api import get_fields
from collective.easyform.interfaces import IEasyForm
from collective.easyform.interfaces import ISaveData
from Products.CMFPlone.utils import safe_unicode


logger = logging.getLogger("collective.easyform.migration")


@implementer(ISerializeToJson)
@adapter(IEasyForm, Interface)
class SerializeToJson(DXContentToJson):
    def __call__(self, version=None, include_items=True):
        result = super(SerializeToJson, self).__call__(version, include_items)
        self.serializeSavedData(result)

        return result

    def serializeSavedData(self, result):
        storage = dict()
        actions = getFieldsInOrder(get_actions(self.context))

        AllFieldsinOrder = getFieldsInOrder(get_fields(self.context))
        included_columns_in_savedata = []
        for column, field in AllFieldsinOrder:
            if "label" not in field.__str__().lower():
                included_columns_in_savedata.append(column)
        included_columns_in_savedata.sort()

        for name, action in actions:
            if ISaveData.providedBy(action):
                serializeable = dict()
                storage[name] = serializeable
                for id, data in action.getSavedFormInputItems():
                    column_names = list(data.keys())
                    column_names.remove("id")
                    column_names.sort()
                    if column_names != included_columns_in_savedata:
                        logger.warning(
                            "Skipped Saveddata row because of mismatch witch current fields in %s",
                            self.context.absolute_url(),
                        )
                        continue
                    try:
                        for key, value in data.items():
                            data[key] = convertBeforeSerialize(value)
                        json.dumps(data)
                        serializeable[id] = data
                    except TypeError:
                        logger.exception(
                            "saved data serialization issue for {}".format(
                                self.context.absolute_url()
                            )
                        )
        if storage:
            result["savedDataStorage"] = storage


def convertBeforeSerialize(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, set):
        return list(value)
    elif isinstance(value, RichTextValue):
        return safe_unicode(value.raw) #raw_encoded
    else:
        return value


@implementer(IDeserializeFromJson)
@adapter(IEasyForm, Interface)
class DeserializeFromJson(DXContentFromJson):
    def __call__(
        self,
        validate_all=False,
        data=None,
        create=False,
    ):  # noqa: ignore=C901

        if data is None:
            data = json_body(self.request)

        super(DeserializeFromJson, self).__call__(validate_all, data, create)

        self.deserializeSavedData(data)
        return self.context

    def deserializeSavedData(self, data):
        if "savedDataStorage" in data:
            storage = data["savedDataStorage"]
            actions = getFieldsInOrder(get_actions(self.context))
            schema = get_fields(self.context)

            AllFieldsinOrder = schema.namesAndDescriptions()
            included_columns_in_savedata = []
            for column, field in AllFieldsinOrder:
                if "label" not in field.__str__().lower():
                    included_columns_in_savedata.append(column)

            for name, action in actions:
                if ISaveData.providedBy(action) and name in storage:
                    savedData = storage[name]
                    for key, value in savedData.items():
                        for name in included_columns_in_savedata:  # schema.names():
                            value[name] = convertAfterDeserialize(
                                schema[name], value[name]
                            )
                        action.setDataRow(int(key), value)


def convertAfterDeserialize(field, value):
    if ISet.providedBy(field):
        return set(value)
    elif IDate.providedBy(field) or IDatetime.providedBy(field):
        return parser.parse(value)
    elif IRichText.providedBy(field):
        return RichTextValue(value)
    else:
        return value
