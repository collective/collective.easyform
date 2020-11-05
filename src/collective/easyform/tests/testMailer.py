# -*- coding: utf-8 -*-
#
# Integeration tests specific to the mailer
#

from collective.easyform.api import get_actions
from collective.easyform.api import get_context
from collective.easyform.api import get_schema
from collective.easyform.api import set_actions
from collective.easyform.api import set_fields
from collective.easyform.interfaces import IActionExtender
from collective.easyform.tests import base
from email.header import decode_header
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedFile
from Products.CMFPlone.utils import safe_unicode

import datetime

try:
    # Python 3
    from email import message_from_bytes
except ImportError:
    # Python 2
    from email import message_from_string as message_from_bytes


class TestFunctions(base.EasyFormTestCase):
    """ Test mailer action """

    def dummy_send(self, mfrom, mto, messageText, immediate=False):
        self.mfrom = mfrom
        self.mto = mto
        if hasattr(messageText, "encode"):
            # It is text instead of bytes.
            messageText = messageText.encode("utf-8")
        self.messageText = messageText
        self.messageBody = b"\n\n".join(messageText.split(b"\n\n")[1:])

    def afterSetUp(self):
        super(TestFunctions, self).afterSetUp()
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.ff1.CSRFProtection = False  # no csrf protection
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        actions = get_actions(self.ff1)
        actions["mailer"].recipient_email = u"mdummy@address.com"
        set_actions(self.ff1, actions)

    def LoadRequestForm(self, **kwargs):
        request = self.layer["request"]
        request.form.clear()
        prefix = "form.widgets."
        for key in kwargs.keys():
            request.form[prefix + key] = kwargs[key]
        return request

    def test_DummyMailer(self):
        """ sanity check; make sure dummy mailer works as expected """

        self.mailhost.send(
            "messageText", mto="dummy@address.com", mfrom="dummy1@address.com"
        )
        self.assertTrue(self.messageText.endswith(b"messageText"))
        self.assertEqual(self.mto, ["dummy@address.com"])
        self.assertIn(b"To: dummy@address.com", self.messageText)
        self.assertEqual(self.mfrom, "dummy1@address.com")
        self.assertIn(b"From: dummy1@address.com", self.messageText)

    def test_Mailer_Basic(self):
        """ Test mailer with dummy_send """

        mailer = get_actions(self.ff1)["mailer"]

        data = {"topic": "test subject", "comments": "test comments"}
        request = self.LoadRequestForm(**data)

        mailer.onSuccess(data, request)

        self.assertIn(b"To: mdummy@address.com", self.messageText)
        self.assertIn(b"Subject: =?utf-8?q?test_subject?=", self.messageText)
        msg = message_from_bytes(self.messageText)
        self.assertIn("test comments", msg.get_payload(decode=False))

    def test_MailerAdditionalHeaders(self):
        """ Test mailer with dummy_send """

        mailer = get_actions(self.ff1)["mailer"]

        data = {"topic": "test subject", "comments": "test comments"}
        request = self.LoadRequestForm(**data)

        mailer.additional_headers = ["Generator: Plone", "Token:   abc  "]

        mailer.onSuccess(data, request)

        self.assertIn(b"Generator: Plone", self.messageText)
        self.assertIn(b"Token: abc", self.messageText)
        self.assertIn(b"To: mdummy@address.com", self.messageText)
        self.assertIn(b"Subject: =?utf-8?q?test_subject?=", self.messageText)
        msg = message_from_bytes(self.messageText)
        self.assertIn("test comments", msg.get_payload(decode=False))

    def test_MailerLongSubject(self):
        """ Test mailer with subject line > 76 chars (Tracker # 84) """

        long_subject = (
            "Now is the time for all good persons to come to"
            "the aid of the quick brown fox."
        )

        mailer = get_actions(self.ff1)["mailer"]

        data = {"topic": long_subject}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = message_from_bytes(self.messageText)
        encoded_subject_header = msg["subject"]
        decoded_header = decode_header(encoded_subject_header)[0][0]

        self.assertEqual(decoded_header, long_subject.encode("utf-8"))

    def test_SubjectDollarReplacement(self):
        """
        Simple subject lines should do ${identifier} replacement from
        request.form -- but only for a basic override.
        """
        mailer = get_actions(self.ff1)["mailer"]
        mailer.msg_subject = "This is my ${topic} now"
        data = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )

        # baseline unchanged
        request = self.LoadRequestForm(**data)
        self.messageText = ""
        mailer.onSuccess(data, request)
        self.assertIn(b"Subject: =?utf-8?q?test_subject?=", self.messageText)

        data2 = dict(
            topic="test ${subject}", replyto="test@test.org", comments="test comments"
        )

        # no substitution on field replacement (default situation)
        request = self.LoadRequestForm(**data2)
        self.messageText = ""
        mailer.onSuccess(data2, request)
        self.assertIn(b"Subject: =?utf-8?q?test_=24=7Bsubject=7D?=", self.messageText)

        # we should get substitution in a basic override
        mailer.subject_field = ""
        request = self.LoadRequestForm(**data)
        self.messageText = ""
        mailer.onSuccess(data, request)
        self.assertIn(
            b"Subject: =?utf-8?q?This_is_my_test_subject_now?=", self.messageText
        )

        # we should get substitution in a basic override
        mailer.msg_subject = "This is my ${untopic} now"
        self.messageText = b""
        mailer.onSuccess(data, request)
        self.assertIn(b"Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=", self.messageText)

        # we don't want substitution on user input
        request = self.LoadRequestForm(**data2)
        self.messageText = b""
        mailer.onSuccess(data2, request)
        self.assertIn(b"Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=", self.messageText)

    def test_TemplateReplacement(self):
        """
        Mail template prologues, epilogues and footers should do ${identifier}
        replacement from request.form -- this is simpler because there are no
        overrides.
        """

        mailer = get_actions(self.ff1)["mailer"]
        mailer.body_pre = "Hello ${topic},"
        mailer.body_post = "Thanks, ${topic}!"
        mailer.body_footer = "Eat my footer, ${topic}."
        data = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )

        # we should get substitution
        request = self.LoadRequestForm(**data)
        self.messageText = b""
        mailer.onSuccess(data, request)
        self.assertIn(b"Hello test subject,", self.messageBody)
        self.assertIn(b"Thanks, test subject!", self.messageBody)
        self.assertIn(b"Eat my footer, test subject.", self.messageBody)

    def test_UTF8Subject(self):
        """ Test mailer with uft-8 encoded subject line """

        utf8_subject = u"Effacer les entrées sauvegardées"
        data = {"topic": utf8_subject}

        mailer = get_actions(self.ff1)["mailer"]
        # fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = message_from_bytes(self.messageText)
        encoded_subject_header = msg["subject"]
        decoded_header = decode_header(encoded_subject_header)[0][0]

        self.assertEqual(safe_unicode(decoded_header), utf8_subject)

    def test_UnicodeSubject(self):
        """ Test mailer with Unicode encoded subject line """
        utf8_subject = u"Effacer les entrées sauvegardées"
        unicode_subject = utf8_subject
        data = {"topic": unicode_subject}

        mailer = get_actions(self.ff1)["mailer"]
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = message_from_bytes(self.messageText)
        encoded_subject_header = msg["subject"]
        decoded_header = decode_header(encoded_subject_header)[0][0]

        self.assertEqual(safe_unicode(decoded_header), utf8_subject)

    def test_Utf8ListSubject(self):
        """ Test mailer with Unicode encoded subject line """
        utf8_subject_list = [u"Effacer les entrées", u"sauvegardées"]
        data = {"topic": utf8_subject_list}
        mailer = get_actions(self.ff1)["mailer"]
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = message_from_bytes(self.messageText)
        encoded_subject_header = msg["subject"]
        decoded_header = decode_header(encoded_subject_header)[0][0]

        self.assertEqual(safe_unicode(decoded_header), ", ".join(utf8_subject_list))

    def test_MailerOverrides(self):
        """ Test mailer override functions """

        mailer = get_actions(self.ff1)["mailer"]
        mailer.subjectOverride = "python: '{0} and {1}'.format('eggs', 'spam')"
        mailer.senderOverride = "string: spam@eggs.com"
        mailer.recipientOverride = "string: eggs@spam.com"
        data = {"topic": "test subject"}
        request = self.LoadRequestForm(**data)

        mailer.onSuccess(data, request)
        self.assertIn(b"Subject: =?utf-8?q?eggs_and_spam?=", self.messageText)
        self.assertIn(b"From: spam@eggs.com", self.messageText)
        self.assertIn(b"To: eggs@spam.com", self.messageText)

    def test_MailerOverridesWithFieldValues(self):
        mailer = get_actions(self.ff1)["mailer"]
        mailer.subjectOverride = "fields/topic"
        mailer.recipientOverride = "fields/replyto"
        data = {"topic": "eggs and spam", "replyto": u"test@test.ts"}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        self.assertIn(b"Subject: =?utf-8?q?eggs_and_spam?=", self.messageText)
        self.assertIn(b"To: test@test.ts", self.messageText)

    def testMultiRecipientOverrideByString(self):
        """ try multiple recipients in recipient override """

        mailer = get_actions(self.ff1)["mailer"]
        mailer.recipientOverride = "string: eggs@spam.com, spam@spam.com"

        data = {"topic": "test subject"}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        self.assertIn(b"To: eggs@spam.com, spam@spam.com", self.messageText)

    def testMultiRecipientOverrideByTuple(self):
        """ try multiple recipients in recipient override """

        mailer = get_actions(self.ff1)["mailer"]
        mailer.recipientOverride = "python: ('eggs@spam.com', 'spam.spam.com')"

        data = {"topic": "test subject"}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        self.assertIn(b"To: eggs@spam.com, spam.spam.com", self.messageText)

    def testRecipientFromRequest(self):
        """ try recipient from designated field  """

        mailer = get_actions(self.ff1)["mailer"]
        mailer.to_field = "replyto"
        mailer.replyto_field = None

        fields = {"topic": "test subject", "replyto": "eggs@spamandeggs.com"}

        request = self.LoadRequestForm(**fields)
        mailer.onSuccess(fields, request)

        self.assertIn(b"To: eggs@spamandeggs.com", self.messageText)

        fields = {
            "topic": "test subject",
            "replyto": ["eggs@spam.com", "spam@spam.com"],
        }
        request = self.LoadRequestForm(**fields)
        mailer.onSuccess(fields, request)

        self.assertTrue(self.messageText.find(b"To: eggs@spam.com, spam@spam.com") > 0)

    def setExecCondition(self, value):
        actions = get_actions(self.ff1)
        IActionExtender(actions["mailer"]).execCondition = value
        set_actions(self.ff1, actions)

    def test_ExecConditions(self):
        """ Test mailer with various exec conditions """

        # if an action adapter's execCondition is filled in and evaluates
        # false, the action adapter should not fire.

        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance

        fields = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        self.LoadRequestForm(**fields)

        self.messageText = b""
        self.setExecCondition("python: False")
        form.processActions(fields)
        self.assertTrue(len(self.messageText) == 0)

        self.messageText = b""
        self.setExecCondition("python: True")
        form.processActions(fields)
        self.assertTrue(len(self.messageText) > 0)

        self.messageText = b""
        self.setExecCondition("python: 1==0")
        form.processActions(fields)
        self.assertTrue(len(self.messageText) == 0)

        # make sure an empty execCondition causes the action to fire
        self.messageText = b""
        self.setExecCondition("")
        form.processActions(fields)
        self.assertTrue(len(self.messageText) > 0)

    def test_selectiveFieldMailing(self):
        """ Test selective inclusion of fields in the mailing """

        mailer = get_actions(self.ff1)["mailer"]
        fields = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        request = self.LoadRequestForm(**fields)

        # make sure all fields are sent unless otherwise specified
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertTrue(
            b"te=\nst subject" in self.messageBody
            and b"test@test.org" in self.messageBody
            and b"test comments" in self.messageBody
        )

        # setting some show fields shouldn't change that
        mailer.showFields = ("topic", "comments")
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertTrue(
            b"te=\nst subject" in self.messageBody
            and b"test@test.org" in self.messageBody
            and b"test comments" in self.messageBody
        )

        # until we turn off the showAll flag
        mailer.showAll = False
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertTrue(
            b"te=\nst subject" in self.messageBody
            and b"test@test.org" not in self.messageBody
            and b"test comments" in self.messageBody
        )

        # check includeEmpties
        mailer.includeEmpties = False

        # first see if everything's still included
        mailer.showAll = True
        self.messageText = b""
        mailer.onSuccess(fields, request)
        # look for labels
        self.assertTrue(
            self.messageBody.find(b"Subject") > 0
            and self.messageBody.find(b"Your E-Mail Address") > 0
            and self.messageBody.find(b"Comments") > 0
        )

        # now, turn off required for a field and leave it empty
        fields = get_schema(self.ff1)
        fields["comments"].required = False
        set_fields(self.ff1, fields)
        fields = {"topic": "test subject", "replyto": "test@test.org"}
        request = self.LoadRequestForm(**fields)
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertIn(b"Subject", self.messageBody)
        self.assertIn(b"Your E-Mail Address", self.messageBody)
        self.assertNotIn(b"Comments", self.messageBody)

    def test_ccOverride(self):
        """ Test override for CC field """

        mailer = get_actions(self.ff1)["mailer"]
        fields = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        request = self.LoadRequestForm(**fields)
        mailer.cc_recipients = "test@testme.com"
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertIn("test@testme.com", self.mto)

        # simple override
        mailer.ccOverride = "string:test@testme.com"
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertIn("test@testme.com", self.mto)

        # list override
        mailer.ccOverride = "python:['test@testme.com', 'test1@testme.com']"
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertTrue(
            "test@testme.com" in self.mto and "test1@testme.com" in self.mto
        )

    def test_bccOverride(self):
        """ Test override for BCC field """
        mailer = get_actions(self.ff1)["mailer"]
        fields = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        request = self.LoadRequestForm(**fields)
        mailer.bcc_recipients = "test@testme.com"
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertIn("test@testme.com", self.mto)

        # simple override
        mailer.bccOverride = "string:test@testme.com"
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertIn("test@testme.com", self.mto)

        # list override
        mailer.bccOverride = "python:['test@testme.com', 'test1@testme.com']"
        self.messageText = b""
        mailer.onSuccess(fields, request)
        self.assertTrue(
            "test@testme.com" in self.mto and "test1@testme.com" in self.mto
        )

    def testNoRecipient(self):
        """
        This is not the feature in easyform as we need recipient in the mailer
        for easyforms. It will not take the default site's recipient.
        """
        mailer = get_actions(self.ff1)["mailer"]
        mailer.recipient_email = u""
        mailer.to_field = None
        mailer.replyto_field = None
        fields = dict(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )

        request = self.LoadRequestForm(**fields)

        self.messageText = b""
        self.assertRaises(ValueError, mailer.onSuccess, fields, request)

    def test_custom_email_template(self):
        """ Test mailer with custom template """
        default_fields = api.content.create(
            self.portal, "File", id="easyform_mail_body_default.pt"
        )
        default_fields.file = NamedFile("Custom e-mail template!")

        mailer = get_actions(self.ff1)["mailer"]
        mailer.onSuccess({}, self.layer["request"])
        self.assertIn(b"Custom e-mail template!", self.messageText)

    def test_MailerXMLAttachments(self):
        """ Test mailer with dummy_send """
        mailer = get_actions(self.ff1)["mailer"]
        mailer.sendXML = True
        mailer.sendCSV = False
        context = get_context(mailer)
        # Test all dexterity field type listed at https://docs.plone.org/external/plone.app.dexterity/docs/reference/fields.html
        fields = dict(
            replyto="test@test.org",
            topic="test subject",
            richtext=RichTextValue(raw="Raw"),
            comments=u"test comments😀",
            datetime=datetime.datetime(2019, 4, 1),
            date=datetime.date(2019, 4, 2),
            delta=datetime.timedelta(1),
            bool=True,
            number=1981,
            floating=3.14,
            tuple=("elemenet1", "element2"),
            list=[1, 2, 3, 4],
            map=dict(fruit="apple"),
            choices=set(["A", "B"]),
            empty_string="",
            zero_value=0,
            none_value=None,
            empty_tuple=(),
            empty_list=[],
            empty_set=set(),
            empty_map=dict(),
        )
        request = self.LoadRequestForm(**fields)
        attachments = mailer.get_attachments(fields, request)
        self.assertEqual(1, len(attachments))
        self.assertIn(
            u"Content-Type: application/xml\nMIME-Version: 1.0\nContent-Transfer-Encoding: base64\nContent-Disposition: attachment",
            mailer.get_mail_text(fields, request, context),
        )
        name, mime, enc, xml = attachments[0]
        output_nodes = (
            b'<field name="replyto">test@test.org</field>',
            b'<field name="topic">test subject</field>',
            b'<field name="richtext">Raw</field>',
            b'<field name="comments">test comments\xf0\x9f\x98\x80</field>',
            b'<field name="datetime">2019/04/01, 00:00:00</field>',
            b'<field name="date">2019/04/02</field>',
            b'<field name="delta">1 day, 0:00:00</field>',
            b'<field name="bool">True</field>',
            b'<field name="number">1981</field>',
            b'<field name="floating">3.14</field>',
            b'<field name="tuple">["elemenet1", "element2"]</field>',
            b'<field name="list">["1", "2", "3", "4"]</field>',
            b'<field name="map">{"fruit": "apple"}</field>',
            b'<field name="empty_string" />',
            b'<field name="zero_value">0</field>',
            b'<field name="none_value" />',
            b'<field name="empty_tuple">[]</field>',
            b'<field name="empty_list">[]</field>',
            b'<field name="empty_set">[]</field>',
            b'<field name="empty_map">{}</field>',
        )

        self.assertIn(b"<?xml version='1.0' encoding='utf-8'?>\n<form>", xml)

        # the order of the nodes can change ... check each line
        for node in output_nodes:
            self.assertIn(node, xml)

        # the order of ["A", "B"] can change ... check separately
        self.assertIn(b'"A"', xml)
        self.assertIn(b'"B"', xml)

    def test_MailerCSVAttachments(self):
        """ Test mailer with dummy_send """
        mailer = get_actions(self.ff1)["mailer"]
        mailer.sendXML = False
        mailer.sendCSV = True
        context = get_context(mailer)
        # Test all dexterity field type listed at https://docs.plone.org/external/plone.app.dexterity/docs/reference/fields.html
        fields = dict(
            topic="test subject",
            replyto="test@test.org",
            richtext=RichTextValue(raw="Raw"),
            comments=u"test comments😀",
            datetime=datetime.datetime(2019, 4, 1),
            date=datetime.date(2019, 4, 2),
            delta=datetime.timedelta(1),
            bool=True,
            number=1981,
            floating=3.14,
            tuple=("elemenet1", "element2"),
            list=[1, 2, 3, 4],
            map=dict(fruit="apple"),
            choices=set(["A", "B"]),
            empty_string="",
            zero_value=0,
            none_value=None,
            empty_tuple=(),
            empty_list=[],
            empty_set=set(),
            empty_map=dict(),
        )
        request = self.LoadRequestForm(**fields)
        attachments = mailer.get_attachments(fields, request)
        self.assertEqual(1, len(attachments))
        self.assertIn(
            u"Content-Type: application/csv\nMIME-Version: 1.0\nContent-Transfer-Encoding: base64\nContent-Disposition: attachment",
            mailer.get_mail_text(fields, request, context),
        )
        name, mime, enc, csv = attachments[0]
        output = (
            b"test@test.org",
            b"test subject",
            b"Raw",
            b"test comments\xf0\x9f\x98\x80",
            b"2019/04/01, 00:00:00",
            b"2019/04/02",
            b"1 day, 0:00:00",
            b"True",
            b"1981",
            b"3.14",
            b'[""elemenet1"", ""element2""]',
            b'[""1"", ""2"", ""3"", ""4""]',
            b'{""fruit"": ""apple""}',
            b"",
            b"0",
            b"",
            b"[]",
            b"[]",
            b"[]",
            b"{}",
        )

        # the order of the columns can change ... check each
        # TODO should really have a header row
        for value in output:
            self.assertIn(value, csv)

        # the order of [""A"", ""B""] can change ... check separately
        self.assertIn(b'""A""', csv)
        self.assertIn(b'""B""', csv)
