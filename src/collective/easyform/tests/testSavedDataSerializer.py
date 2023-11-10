# -*- coding: utf-8 -*-
from datetime import datetime, date
from plone.app.textfield import RichText, RichTextValue
from .testSaver import BaseSaveData, FakeRequest
from collective.easyform.api import get_actions, set_fields
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import getMultiAdapter
import json
from zope.interface import Interface
from plone.supermodel import model
from plone import schema

class ISpecialConverters(model.Schema, Interface):

    datetime = schema.Datetime()
    date = schema.Date()
    set = schema.Set()
    rich = RichText()
    

class SavedDataSerializerTestCase(BaseSaveData):  

    def testDefaultFormDataSerialization(self):
        self.request = self.layer["request"]
        self.createSaver()
        saver = get_actions(self.ff1)["saver"]
        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, "saver")
        view = view.publishTraverse(view.request, "data")
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {"items": 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]["id"], item[0])
        self.assertEqual(item[1]["topic"], "test subject")
        self.assertEqual(item[1]["replyto"], "test@test.org")
        self.assertEqual(item[1]["comments"], "test comments")
        obj = self.serialize(self.ff1)
        self.assertIn("savedDataStorage", obj)
        self.assertIn("test subject", json.dumps(obj))
        self.assertIn("test@test.org", json.dumps(obj))
        self.assertIn("test comments", json.dumps(obj))

    def testSpecialConverterFormDataSerialization(self):
        self.request = self.layer["request"]
        set_fields(self.ff1, ISpecialConverters)
        self.createSaver()
        saver = get_actions(self.ff1)["saver"]
        request = FakeRequest(
            datetime=datetime(1999, 12, 25, 19, 0, 0),
            date=date(2004, 11, 30),
            set=set(["please", "kill", "me"]),
            rich=RichTextValue(raw=u"<div><b>testing is fùn</b> says Michaël</div>"),
        )
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, "saver")
        obj = self.serialize(self.ff1)
        self.assertIn("savedDataStorage", obj)
        self.assertIn("1999-12-25T19:00:00", json.dumps(obj))
        self.assertIn("2004-11-30", json.dumps(obj))
        self.assertIn("please", json.dumps(obj))
        self.assertIn("kill", json.dumps(obj))
        self.assertIn("me", json.dumps(obj))
        self.assertIn(u"<div><b>testing is f\\u00f9n</b> says Micha\\u00ebl</div>", json.dumps(obj))

    def testShowFieldsFormDataSerialization(self):
        self.request = self.layer["request"]
        self.createSaver()

        ## set showfields
        extra_showfields = '\n      <showFields>\n        <element>topic</element>\n        <element>comments</element>\n      </showFields>'
        idx = self.ff1.actions_model.index('<title>Saver</title>\n')
        self.ff1.actions_model = self.ff1.actions_model[:idx] + extra_showfields + self.ff1.actions_model[idx:]
        saver = get_actions(self.ff1)["saver"]
        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        saver.onSuccess(request.form, request)

        obj = self.serialize(self.ff1)
        self.assertIn("savedDataStorage", obj)
        self.assertIn("test subject", json.dumps(obj))
        self.assertNotIn("test@test.org", json.dumps(obj))
        self.assertIn("test comments", json.dumps(obj))

    def testExtraDataFormDataSerialization(self):
        self.request = self.layer["request"]
        self.createSaver()

        ## set extradata and showfields
        extra_showfields = '\n      <ExtraData>\n        <element>dt</element>\n        <element>HTTP_X_FORWARDED_FOR</element>\n      </ExtraData>'
        idx = self.ff1.actions_model.index('<title>Saver</title>\n')
        self.ff1.actions_model = self.ff1.actions_model[:idx] + extra_showfields + self.ff1.actions_model[idx:]
        saver = get_actions(self.ff1)["saver"]
        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        saver.onSuccess(request.form, request)

        obj = self.serialize(self.ff1)
        self.assertIn("savedDataStorage", obj)
        self.assertIn("test subject", json.dumps(obj))
        self.assertIn("test@test.org", json.dumps(obj))
        self.assertIn("test comments", json.dumps(obj))
        self.assertIn("dt", json.dumps(obj))
        self.assertIn("HTTP_X_FORWARDED_FOR", json.dumps(obj))

    def serialize(self, obj=None):
        if obj is None:
            obj = self.portal.doc1
        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer()


class SavedDataDeserializerTestCase(BaseSaveData):

    def testDefaultFormDataDeserialization(self):
        BODY = ( '{"actions_model": "<model '
                'xmlns:i18n=\\"http://xml.zope.org/namespaces/i18n\\" '
                'xmlns:marshal=\\"http://namespaces.plone.org/supermodel/marshal\\" '
                'xmlns:form=\\"http://namespaces.plone.org/supermodel/form\\" '
                'xmlns:security=\\"http://namespaces.plone.org/supermodel/security\\" '
                'xmlns:users=\\"http://namespaces.plone.org/supermodel/users\\" '
                'xmlns:lingua=\\"http://namespaces.plone.org/supermodel/lingua\\" '
                'xmlns:easyform=\\"http://namespaces.plone.org/supermodel/easyform\\" '
                'xmlns=\\"http://namespaces.plone.org/supermodel/schema\\" '
                'i18n:domain=\\"collective.easyform\\">\\n  <schema>\\n   <field '
                'name=\\"saver\\" type=\\"collective.easyform.actions.SaveData\\">\\n      '
                '<title>Saver</title>\\n    </field>\\n  </schema>\\n</model>",'
                '"savedDataStorage": '
                '{"saver": {"1658237759974": {"topic": "test subject", "replyto": '
                '"test@test.org", "comments": "test comments", "id": 1658237759974}}}}')
        self.deserialize(body=BODY, context=self.ff1)
        saver = get_actions(self.ff1)["saver"]
        data = saver.getSavedFormInput()[0]
        self.assertIn("topic", data)
        self.assertEqual("test subject", data['topic'])
        self.assertIn("replyto", data)
        self.assertEqual("test@test.org", data['replyto'])
        self.assertIn("comments", data)
        self.assertEqual("test comments", data['comments'])

    def testSpecialConvertersFormDataDeserialization(self):
        BODY = ( '{"fields_model": "<model xmlns:i18n=\\"http://xml.zope.org/namespaces/i18n\\" '
                'xmlns:marshal=\\"http://namespaces.plone.org/supermodel/marshal\\" '
                'xmlns:form=\\"http://namespaces.plone.org/supermodel/form\\" '
                'xmlns:security=\\"http://namespaces.plone.org/supermodel/security\\" '
                'xmlns:users=\\"http://namespaces.plone.org/supermodel/users\\" '
                'xmlns:lingua=\\"http://namespaces.plone.org/supermodel/lingua\\" '
                'xmlns:easyform=\\"http://namespaces.plone.org/supermodel/easyform\\" '
                'xmlns=\\"http://namespaces.plone.org/supermodel/schema\\">\\n  <schema '
                'based-on=\\"zope.interface.Interface\\">\\n    <field name=\\"datetime\\" '
                'type=\\"zope.schema.Datetime\\"/>\\n    <field name=\\"date\\" '
                'type=\\"zope.schema.Date\\"/>\\n    <field name=\\"set\\" '
                'type=\\"zope.schema.Set\\"/>\\n    <field name=\\"rich\\" '
                'type=\\"plone.app.textfield.RichText\\"/>\\n  </schema>\\n</model>", '
                '"actions_model": "<model '
                'xmlns:i18n=\\"http://xml.zope.org/namespaces/i18n\\" '
                'xmlns:marshal=\\"http://namespaces.plone.org/supermodel/marshal\\" '
                'xmlns:form=\\"http://namespaces.plone.org/supermodel/form\\" '
                'xmlns:security=\\"http://namespaces.plone.org/supermodel/security\\" '
                'xmlns:users=\\"http://namespaces.plone.org/supermodel/users\\" '
                'xmlns:lingua=\\"http://namespaces.plone.org/supermodel/lingua\\" '
                'xmlns:easyform=\\"http://namespaces.plone.org/supermodel/easyform\\" '
                'xmlns=\\"http://namespaces.plone.org/supermodel/schema\\" '
                'i18n:domain=\\"collective.easyform\\">\\n  <schema>\\n   <field '
                'name=\\"saver\\" type=\\"collective.easyform.actions.SaveData\\">\\n      '
                '<title>Saver</title>\\n    </field>\\n  </schema>\\n</model>",'
                '"savedDataStorage": '
                '{"saver": {"1658240583228": {"datetime": "1999-12-25T19:00:00", "date": '
                '"2004-11-30", "set": ["please", "me", "kill"], "rich": "<div><b>testing is '
                'f\\u00f9n</b> says Micha\\u00ebl</div>", "id": 1658240583228}}}}')

        self.deserialize(body=BODY, context=self.ff1)
        saver = get_actions(self.ff1)["saver"]
        data = saver.getSavedFormInput()[0]
        self.assertIn("datetime", data)
        self.assertEqual(datetime(1999, 12, 25, 19, 0, 0), data['datetime'])
        self.assertIn("date", data)
        self.assertEqual(datetime(2004, 11, 30), data['date'])
        self.assertIn("set", data)
        setdata = list(data['set'])
        setdata.sort()
        self.assertEqual(["kill", "me", "please"], setdata)
        self.assertIn("rich", data)
        self.assertEqual(u"<div><b>testing is fùn</b> says Michaël</div>", data['rich'].raw)

    def testShowFieldsFormDataDeserialization(self):
        BODY = ( '{"actions_model": "<model '
            'xmlns:i18n=\\"http://xml.zope.org/namespaces/i18n\\" '
            'xmlns:marshal=\\"http://namespaces.plone.org/supermodel/marshal\\" '
            'xmlns:form=\\"http://namespaces.plone.org/supermodel/form\\" '
            'xmlns:security=\\"http://namespaces.plone.org/supermodel/security\\" '
            'xmlns:users=\\"http://namespaces.plone.org/supermodel/users\\" '
            'xmlns:lingua=\\"http://namespaces.plone.org/supermodel/lingua\\" '
            'xmlns:easyform=\\"http://namespaces.plone.org/supermodel/easyform\\" '
            'xmlns=\\"http://namespaces.plone.org/supermodel/schema\\" '
            'i18n:domain=\\"collective.easyform\\">\\n  <schema>\\n   <field '
            'name=\\"saver\\" type=\\"collective.easyform.actions.SaveData\\">\\n      '
            '<showFields>\\n        <element>topic</element>\\n        <element>comments</element>\\n      </showFields>\\n      '
            '<title>Saver</title>\\n    </field>\\n  </schema>\\n</model>",'
            '"savedDataStorage": '
            '{"saver": {"1658237759974": {"topic": "test subject", "replyto": '
            '"test@test.org", "comments": "test comments", "id": 1658237759974}}}}')

        self.deserialize(body=BODY, context=self.ff1)
        saver = get_actions(self.ff1)["saver"]
        data = saver.getSavedFormInput()[0]
        self.assertIn("topic", data)
        self.assertEqual("test subject", data['topic'])
        self.assertNotIn("replyto", data)
        self.assertIn("comments", data)
        self.assertEqual("test comments", data['comments'])

    def testExtraDataFormDataDeserialization(self):
        BODY = ( '{"actions_model": "<model '
            'xmlns:i18n=\\"http://xml.zope.org/namespaces/i18n\\" '
            'xmlns:marshal=\\"http://namespaces.plone.org/supermodel/marshal\\" '
            'xmlns:form=\\"http://namespaces.plone.org/supermodel/form\\" '
            'xmlns:security=\\"http://namespaces.plone.org/supermodel/security\\" '
            'xmlns:users=\\"http://namespaces.plone.org/supermodel/users\\" '
            'xmlns:lingua=\\"http://namespaces.plone.org/supermodel/lingua\\" '
            'xmlns:easyform=\\"http://namespaces.plone.org/supermodel/easyform\\" '
            'xmlns=\\"http://namespaces.plone.org/supermodel/schema\\" '
            'i18n:domain=\\"collective.easyform\\">\\n  <schema>\\n   <field '
            'name=\\"saver\\" type=\\"collective.easyform.actions.SaveData\\">\\n      '
            '<ExtraData>\\n        <element>td</element>\\n        <element>HTTP_X_FORWARDED_FOR</element>\\n      </ExtraData>\\n      '
            '<title>Saver</title>\\n    </field>\\n  </schema>\\n</model>",'
            '"savedDataStorage": '
            '{"saver": {"1658237759974": {"topic": "test subject", "replyto": '
            '"test@test.org", "comments": "test comments", "id": 1658237759974,'
            '"HTTP_X_FORWARDED_FOR": "", "dt": "2023/11/10 09:54:5.924947 GMT+1"}}}}')

        self.deserialize(body=BODY, context=self.ff1)
        saver = get_actions(self.ff1)["saver"]
        data = saver.getSavedFormInput()[0]
        self.assertIn("topic", data)
        self.assertEqual("test subject", data['topic'])
        self.assertIn("replyto", data)
        self.assertEqual("test@test.org", data['replyto'])
        self.assertIn("comments", data)
        self.assertEqual("test comments", data['comments'])
        self.assertIn("dt", data)
        self.assertEqual("2023/11/10 09:54:5.924947 GMT+1", data['dt'])
        self.assertIn("HTTP_X_FORWARDED_FOR", data)
    
    def deserialize(self, body="{}", validate_all=False, context=None, create=False):
        self.request = self.layer["request"]
        self.request["BODY"] = body
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all, create=create)