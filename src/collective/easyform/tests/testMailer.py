# -*- coding: utf-8 -*-
#
# Integeration tests specific to the mailer
#

from collective.easyform.api import get_actions
from collective.easyform.api import get_schema
from collective.easyform.api import set_actions
from collective.easyform.api import set_fields
from collective.easyform.interfaces import IActionExtender
from collective.easyform.tests import base
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedFile

import email


class TestFunctions(base.EasyFormTestCase):
    """ Test mailer action """

    def dummy_send(self, mfrom, mto, messageText, immediate=False):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText
        self.messageBody = '\n\n'.join(messageText.split('\n\n')[1:])

    def afterSetUp(self):
        super(TestFunctions, self).afterSetUp()
        self.folder.invokeFactory('EasyForm', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.CSRFProtection = False  # no csrf protection
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        actions = get_actions(self.ff1)
        actions['mailer'].recipient_email = u'mdummy@address.com'
        set_actions(self.ff1, actions)

    def LoadRequestForm(self, **kwargs):
        request = self.layer['request']
        request.form.clear()
        prefix = 'form.widgets.'
        for key in kwargs.keys():
            request.form[prefix + key] = kwargs[key]
        return request

    def test_DummyMailer(self):
        """ sanity check; make sure dummy mailer works as expected """

        self.mailhost.send(
            'messageText', mto='dummy@address.com', mfrom='dummy1@address.com')
        self.assertTrue(self.messageText.endswith('messageText'))
        self.assertEqual(self.mto, ['dummy@address.com'])
        self.assertIn('To: dummy@address.com', self.messageText)
        self.assertEqual(self.mfrom, 'dummy1@address.com')
        self.assertIn('From: dummy1@address.com', self.messageText)

    def test_Mailer_Basic(self):
        """ Test mailer with dummy_send """

        mailer = get_actions(self.ff1)['mailer']

        data = {'topic': 'test subject', 'comments': 'test comments'}
        request = self.LoadRequestForm(**data)

        mailer.onSuccess(data, request)

        self.assertIn('To: mdummy@address.com', self.messageText)
        self.assertIn(
            'Subject: =?utf-8?q?test_subject?=', self.messageText)
        msg = email.message_from_string(self.messageText)
        self.assertIn(
            'test comments', msg.get_payload(decode=True))

    def test_MailerAdditionalHeaders(self):
        """ Test mailer with dummy_send """

        mailer = get_actions(self.ff1)['mailer']

        data = {'topic': 'test subject', 'comments': 'test comments'}
        request = self.LoadRequestForm(**data)

        mailer.additional_headers = [
            'Generator: Plone',
            'Token:   abc  ',
        ]

        mailer.onSuccess(data, request)

        self.assertIn('Generator: Plone', self.messageText)
        self.assertIn('Token: abc', self.messageText)
        self.assertIn('To: mdummy@address.com', self.messageText)
        self.assertIn(
            'Subject: =?utf-8?q?test_subject?=', self.messageText)
        msg = email.message_from_string(self.messageText)
        self.assertIn(
            'test comments', msg.get_payload(decode=True))

    def test_MailerLongSubject(self):
        """ Test mailer with subject line > 76 chars (Tracker # 84) """

        long_subject = (
            'Now is the time for all good persons to come to'
            'the aid of the quick brown fox.'
        )

        mailer = get_actions(self.ff1)['mailer']

        data = {'topic': long_subject}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(
            encoded_subject_header)[0][0]

        self.assertEqual(decoded_header, long_subject)

    def test_SubjectDollarReplacement(self):
        """
        Simple subject lines should do ${identifier} replacement from
        request.form -- but only for a basic override.
        """
        mailer = get_actions(self.ff1)['mailer']
        mailer.msg_subject = 'This is my ${topic} now'
        data = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        # baseline unchanged
        request = self.LoadRequestForm(**data)
        self.messageText = ''
        mailer.onSuccess(data, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?test_subject?=') > 0)

        data2 = dict(
            topic='test ${subject}',
            replyto='test@test.org',
            comments='test comments'
        )

        # no substitution on field replacement (default situation)
        request = self.LoadRequestForm(**data2)
        self.messageText = ''
        mailer.onSuccess(data2, request)
        self.assertIn(
            'Subject: =?utf-8?q?test_=24=7Bsubject=7D?=', self.messageText)

        # we should get substitution in a basic override
        mailer.subject_field = ''
        request = self.LoadRequestForm(**data)
        self.messageText = ''
        mailer.onSuccess(data, request)
        self.assertIn(
            'Subject: =?utf-8?q?This_is_my_test_subject_now?=',
            self.messageText)

        # we should get substitution in a basic override
        mailer.msg_subject = 'This is my ${untopic} now'
        self.messageText = ''
        mailer.onSuccess(data, request)
        self.assertIn(
            'Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=',
            self.messageText)

        # we don't want substitution on user input
        request = self.LoadRequestForm(**data2)
        self.messageText = ''
        mailer.onSuccess(data2, request)
        self.assertIn(
            'Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=',
            self.messageText)

    def test_TemplateReplacement(self):
        """
        Mail template prologues, epilogues and footers should do ${identifier}
        replacement from request.form -- this is simpler because there are no
        overrides.
        """

        mailer = get_actions(self.ff1)['mailer']
        mailer.body_pre = 'Hello ${topic},'
        mailer.body_post = 'Thanks, ${topic}!'
        mailer.body_footer = 'Eat my footer, ${topic}.'
        data = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        # we should get substitution
        request = self.LoadRequestForm(**data)
        self.messageText = ''
        mailer.onSuccess(data, request)
        self.assertIn('Hello test subject,', self.messageBody)
        self.assertIn('Thanks, test subject!', self.messageBody)
        self.assertIn('Eat my footer, test subject.', self.messageBody)

    def test_UTF8Subject(self):
        """ Test mailer with uft-8 encoded subject line """

        utf8_subject = 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'
        data = {'topic': utf8_subject}

        mailer = get_actions(self.ff1)['mailer']
        # fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(
            encoded_subject_header)[0][0]

        self.assertEqual(decoded_header, utf8_subject)

    def test_UnicodeSubject(self):
        """ Test mailer with Unicode encoded subject line """
        utf8_subject = 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'
        unicode_subject = utf8_subject.decode('UTF-8')
        data = {'topic': unicode_subject}

        mailer = get_actions(self.ff1)['mailer']
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(
            encoded_subject_header)[0][0]

        self.assertEqual(decoded_header, utf8_subject)

    def test_Utf8ListSubject(self):
        """ Test mailer with Unicode encoded subject line """
        utf8_subject_list = [
            'Effacer les entr\xc3\xa9es',
            'sauvegard\xc3\xa9es'
        ]
        data = {'topic': utf8_subject_list}
        mailer = get_actions(self.ff1)['mailer']
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(
            encoded_subject_header)[0][0]

        self.assertEqual(
            decoded_header,
            ', '.join(utf8_subject_list))

    def test_MailerOverrides(self):
        """ Test mailer override functions """

        mailer = get_actions(self.ff1)['mailer']
        mailer.subjectOverride = "python: '{0} and {1}'.format('eggs', 'spam')"
        mailer.senderOverride = 'string: spam@eggs.com'
        mailer.recipientOverride = 'string: eggs@spam.com'
        data = {'topic': 'test subject'}
        request = self.LoadRequestForm(**data)

        mailer.onSuccess(data, request)
        self.assertIn('Subject: =?utf-8?q?eggs_and_spam?=', self.messageText)
        self.assertIn('From: spam@eggs.com', self.messageText)
        self.assertIn('To: eggs@spam.com', self.messageText)

    def test_MailerOverridesWithFieldValues(self):
        mailer = get_actions(self.ff1)['mailer']
        mailer.subjectOverride = 'fields/topic'
        mailer.recipientOverride = 'fields/replyto'
        data = {'topic': 'eggs and spam', 'replyto': u'test@test.ts'}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        self.assertIn('Subject: =?utf-8?q?eggs_and_spam?=', self.messageText)
        self.assertIn('To: test@test.ts', self.messageText)

    def testMultiRecipientOverrideByString(self):
        """ try multiple recipients in recipient override """

        mailer = get_actions(self.ff1)['mailer']
        mailer.recipientOverride = 'string: eggs@spam.com, spam@spam.com'

        data = {'topic': 'test subject'}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        self.assertIn('To: eggs@spam.com, spam@spam.com', self.messageText)

    def testMultiRecipientOverrideByTuple(self):
        """ try multiple recipients in recipient override """

        mailer = get_actions(self.ff1)['mailer']
        mailer.recipientOverride = "python: ('eggs@spam.com', 'spam.spam.com')"

        data = {'topic': 'test subject'}
        request = self.LoadRequestForm(**data)
        mailer.onSuccess(data, request)

        self.assertIn('To: eggs@spam.com, spam.spam.com', self.messageText)

    def testRecipientFromRequest(self):
        """ try recipient from designated field  """

        mailer = get_actions(self.ff1)['mailer']
        mailer.to_field = 'replyto'
        mailer.replyto_field = None

        fields = {'topic': 'test subject', 'replyto': 'eggs@spamandeggs.com'}

        request = self.LoadRequestForm(**fields)
        mailer.onSuccess(fields, request)

        self.assertIn('To: eggs@spamandeggs.com', self.messageText)

        fields = {'topic': 'test subject',
                  'replyto': ['eggs@spam.com', 'spam@spam.com']}
        request = self.LoadRequestForm(**fields)
        mailer.onSuccess(fields, request)

        self.assertTrue(self.messageText.find(
            'To: eggs@spam.com, spam@spam.com') > 0)

    def setExecCondition(self, value):
        actions = get_actions(self.ff1)
        IActionExtender(actions['mailer']).execCondition = value
        set_actions(self.ff1, actions)

    def test_ExecConditions(self):
        """ Test mailer with various exec conditions """

        # if an action adapter's execCondition is filled in and evaluates
        # false, the action adapter should not fire.

        view = self.ff1.restrictedTraverse('view')
        form = view.form_instance

        fields = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        self.LoadRequestForm(**fields)

        self.messageText = ''
        self.setExecCondition('python: False')
        form.processActions(fields)
        self.assertTrue(len(self.messageText) == 0)

        self.messageText = ''
        self.setExecCondition('python: True')
        form.processActions(fields)
        self.assertTrue(len(self.messageText) > 0)

        self.messageText = ''
        self.setExecCondition('python: 1==0')
        form.processActions(fields)
        self.assertTrue(len(self.messageText) == 0)

        # make sure an empty execCondition causes the action to fire
        self.messageText = ''
        self.setExecCondition('')
        form.processActions(fields)
        self.assertTrue(len(self.messageText) > 0)

    def test_selectiveFieldMailing(self):
        """ Test selective inclusion of fields in the mailing """

        mailer = get_actions(self.ff1)['mailer']
        fields = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        request = self.LoadRequestForm(**fields)

        # make sure all fields are sent unless otherwise specified
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertTrue(
            'te=\nst subject' in self.messageBody and
            'test@test.org' in self.messageBody and
            'test comments' in self.messageBody
        )

        # setting some show fields shouldn't change that
        mailer.showFields = ('topic', 'comments',)
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertTrue(
            'te=\nst subject' in self.messageBody and
            'test@test.org' in self.messageBody and
            'test comments' in self.messageBody
        )

        # until we turn off the showAll flag
        mailer.showAll = False
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertTrue(
            'te=\nst subject' in self.messageBody and
            'test@test.org' not in self.messageBody and
            'test comments' in self.messageBody
        )

        # check includeEmpties
        mailer.includeEmpties = False

        # first see if everything's still included
        mailer.showAll = True
        self.messageText = ''
        mailer.onSuccess(fields, request)
        # look for labels
        self.assertTrue(
            self.messageBody.find('Subject') > 0 and
            self.messageBody.find('Your E-Mail Address') > 0 and
            self.messageBody.find('Comments') > 0
        )

        # now, turn off required for a field and leave it empty
        fields = get_schema(self.ff1)
        fields['comments'].required = False
        set_fields(self.ff1, fields)
        fields = {'topic': 'test subject', 'replyto': 'test@test.org'}
        request = self.LoadRequestForm(**fields)
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertIn('Subject', self.messageBody)
        self.assertIn('Your E-Mail Address', self.messageBody)
        self.assertNotIn('Comments', self.messageBody)

    def test_ccOverride(self):
        """ Test override for CC field """

        mailer = get_actions(self.ff1)['mailer']
        fields = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        request = self.LoadRequestForm(**fields)
        mailer.cc_recipients = 'test@testme.com'
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertIn('test@testme.com', self.mto)

        # simple override
        mailer.ccOverride = 'string:test@testme.com'
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertIn('test@testme.com', self.mto)

        # list override
        mailer.ccOverride = "python:['test@testme.com', 'test1@testme.com']"
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertTrue(
            'test@testme.com' in self.mto and
            'test1@testme.com' in self.mto
        )

    def test_bccOverride(self):
        """ Test override for BCC field """
        mailer = get_actions(self.ff1)['mailer']
        fields = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        request = self.LoadRequestForm(**fields)
        mailer.bcc_recipients = 'test@testme.com'
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertIn('test@testme.com', self.mto)

        # simple override
        mailer.bccOverride = 'string:test@testme.com'
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertIn('test@testme.com', self.mto)

        # list override
        mailer.bccOverride = "python:['test@testme.com', 'test1@testme.com']"
        self.messageText = ''
        mailer.onSuccess(fields, request)
        self.assertTrue(
            'test@testme.com' in self.mto and
            'test1@testme.com' in self.mto
        )

    def testNoRecipient(self):
        """
        This is not the feature in easyform as we need recipient in the mailer
        for easyforms. It will not take the default site's recipient.
        """
        mailer = get_actions(self.ff1)['mailer']
        mailer.recipient_email = u''
        mailer.to_field = None
        mailer.replyto_field = None
        fields = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        request = self.LoadRequestForm(**fields)

        self.messageText = ''
        self.assertRaises(ValueError, mailer.onSuccess, fields, request)

    def test_custom_email_template(self):
        """ Test mailer with custom template """
        default_fields = api.content.create(
            self.portal, 'File', id='easyform_mail_body_default.pt')
        default_fields.file = NamedFile('Custom e-mail template!')

        mailer = get_actions(self.ff1)['mailer']
        mailer.onSuccess({}, self.layer['request'])
        self.assertIn(u'Custom e-mail template!', self.messageText)

    def test_MailerXMLAttachments(self):
        """ Test mailer with dummy_send """
        mailer = get_actions(self.ff1)['mailer']
        mailer.sendXML = True
        mailer.sendCSV = False
        fields = dict(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments',
            choices=set(['A', 'B']),
            richtext=RichTextValue(raw='Raw')
        )
        request = self.LoadRequestForm(**fields)
        attachments = mailer.get_attachments(fields, request)
        self.assertEqual(1, len(attachments))
