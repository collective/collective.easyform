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

import email


class TestFunctions(base.EasyFormTestCase):

    """ test ya_gpg.py """

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
        form = self.app.REQUEST.form
        form.clear()
        for key in kwargs.keys():
            form[key] = kwargs[key]
        return self.app.REQUEST

    def test_DummyMailer(self):
        """ sanity check; make sure dummy mailer works as expected """

        self.mailhost.send(
            'messageText', mto='dummy@address.com', mfrom='dummy1@address.com')
        self.assertTrue(self.messageText.endswith('messageText'))
        self.assertEqual(self.mto, ['dummy@address.com'])
        self.assertTrue(self.messageText.find('To: dummy@address.com') > 0)
        self.assertEqual(self.mfrom, 'dummy1@address.com')
        self.assertTrue(self.messageText.find('From: dummy1@address.com') > 0)

    def test_Mailer(self):
        """ Test mailer with dummy_send """

        mailer = get_actions(self.ff1)['mailer']

        request = self.LoadRequestForm(
            topic='test subject', comments='test comments')

        mailer.onSuccess(request.form, request)

        self.assertTrue(self.messageText.find('To: mdummy@address.com') > 0)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?test_subject?=') > 0)
        msg = email.message_from_string(self.messageText)
        self.assertTrue(
            msg.get_payload(decode=True).find('test comments') > 0)

    def test_MailerAdditionalHeaders(self):
        """ Test mailer with dummy_send """

        mailer = get_actions(self.ff1)['mailer']

        request = self.LoadRequestForm(
            topic='test subject', comments='test comments')

        mailer.additional_headers = [
            'Generator: Plone',
            'Token:   abc  ',
        ]

        mailer.onSuccess(request.form, request)

        self.assertTrue(self.messageText.find('Generator: Plone') > 0)
        self.assertTrue(self.messageText.find('Token: abc') > 0)
        self.assertTrue(self.messageText.find('To: mdummy@address.com') > 0)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?test_subject?=') > 0)
        msg = email.message_from_string(self.messageText)
        self.assertTrue(
            msg.get_payload(decode=True).find('test comments') > 0)

    def test_MailerLongSubject(self):
        """ Test mailer with subject line > 76 chars (Tracker # 84) """

        long_subject = (
            'Now is the time for all good persons to come to'
            'the aid of the quick brown fox.'
        )

        mailer = get_actions(self.ff1)['mailer']
        # fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(topic=long_subject)
        mailer.onSuccess(request.form, request)

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

        # baseline unchanged
        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?test_subject?=') > 0)

        # no substitution on field replacement (default situation)
        request = self.LoadRequestForm(
            topic='test ${subject}',
            replyto='test@test.org',
            comments='test comments'
        )
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?test_=24=7Bsubject=7D?=') > 0)

        # we should get substitution in a basic override
        mailer.subject_field = ''
        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?This_is_my_test_subject_now?=') > 0)

        # we should get substitution in a basic override
        mailer.msg_subject = 'This is my ${untopic} now'
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=') > 0)

        # we don't want substitution on user input
        request = self.LoadRequestForm(
            topic='test ${subject}',
            replyto='test@test.org',
            comments='test comments'
        )
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=') > 0)

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

        # we should get substitution
        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageBody.find('Hello test subject,') > 0)
        self.assertTrue(self.messageBody.find('Thanks, test subject!') > 0)
        self.assertTrue(self.messageBody.find(
            'Eat my footer, test subject.') > 0)

    def test_UTF8Subject(self):
        """ Test mailer with uft-8 encoded subject line """

        utf8_subject = 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'

        mailer = get_actions(self.ff1)['mailer']
        # fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(topic=utf8_subject)
        mailer.onSuccess(request.form, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(
            encoded_subject_header)[0][0]

        self.assertEqual(decoded_header, utf8_subject)

    def test_UnicodeSubject(self):
        """ Test mailer with Unicode encoded subject line """

        utf8_subject = 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'
        unicode_subject = utf8_subject.decode('UTF-8')

        mailer = get_actions(self.ff1)['mailer']
        # fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(topic=unicode_subject)
        mailer.onSuccess(request.form, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(
            encoded_subject_header)[0][0]

        self.assertEqual(decoded_header, utf8_subject)

    def test_MailerOverrides(self):
        """ Test mailer override functions """

        mailer = get_actions(self.ff1)['mailer']
        mailer.subjectOverride = "python: '{0} and {1}'.format('eggs', 'spam')"
        mailer.senderOverride = 'string: spam@eggs.com'
        mailer.recipientOverride = 'string: eggs@spam.com'

        # fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic='test subject')

        mailer.onSuccess(request.form, request)
        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?eggs_and_spam?=') > 0)
        self.assertTrue(self.messageText.find('From: spam@eggs.com') > 0)
        self.assertTrue(self.messageText.find('To: eggs@spam.com') > 0)

    def test_MailerOverridesWithFieldValues(self):
        mailer = get_actions(self.ff1)['mailer']
        mailer.subjectOverride = 'fields/topic'
        mailer.recipientOverride = 'fields/replyto'

        request = self.LoadRequestForm(
            topic='eggs and spam',
            replyto=u'test@test.ts'
        )
        mailer.onSuccess(request.form, request)

        self.assertTrue(self.messageText.find(
            'Subject: =?utf-8?q?eggs_and_spam?=') > 0)
        self.assertTrue(self.messageText.find('To: test@test.ts') > 0)

    def testMultiRecipientOverrideByString(self):
        """ try multiple recipients in recipient override """

        mailer = get_actions(self.ff1)['mailer']
        mailer.recipientOverride = 'string: eggs@spam.com, spam@spam.com'

        # fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic='test subject')

        mailer.onSuccess(request.form, request)

        self.assertTrue(self.messageText.find(
            'To: eggs@spam.com, spam@spam.com') > 0)

    def testMultiRecipientOverrideByTuple(self):
        """ try multiple recipients in recipient override """

        mailer = get_actions(self.ff1)['mailer']
        mailer.recipientOverride = "python: ('eggs@spam.com', 'spam.spam.com')"

        # fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic='test subject')

        mailer.onSuccess(request.form, request)

        self.assertTrue(self.messageText.find(
            'To: eggs@spam.com, spam.spam.com') > 0)

    def testRecipientFromRequest(self):
        """ try recipient from designated field  """

        mailer = get_actions(self.ff1)['mailer']
        mailer.to_field = 'replyto'
        mailer.replyto_field = None

        # fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(
            topic='test subject', replyto='eggs@spamandeggs.com')

        mailer.onSuccess(request.form, request)

        self.assertTrue(
            self.messageText.find('To: eggs@spamandeggs.com') > 0)

        request = self.LoadRequestForm(
            topic='test subject', replyto=['eggs@spam.com', 'spam@spam.com'])

        mailer.onSuccess(request.form, request)

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

        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        self.messageText = ''
        self.setExecCondition('python: False')
        form.processActions(request.form)
        self.assertTrue(len(self.messageText) == 0)

        self.messageText = ''
        self.setExecCondition('python: True')
        form.processActions(request.form)
        self.assertTrue(len(self.messageText) > 0)

        self.messageText = ''
        self.setExecCondition('python: 1==0')
        form.processActions(request.form)
        self.assertTrue(len(self.messageText) == 0)

        # make sure an empty execCondition causes the action to fire
        self.messageText = ''
        self.setExecCondition('')
        form.processActions(request.form)
        self.assertTrue(len(self.messageText) > 0)

    def test_selectiveFieldMailing(self):
        """ Test selective inclusion of fields in the mailing """

        mailer = get_actions(self.ff1)['mailer']
        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        # make sure all fields are sent unless otherwise specified
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            self.messageBody.find('test subject') > 0 and
            self.messageBody.find('test@test.org') > 0 and
            self.messageBody.find('test comments') > 0
        )

        # setting some show fields shouldn't change that
        mailer.showFields = ('topic', 'comments',)
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            self.messageBody.find('test subject') > 0 and
            self.messageBody.find('test@test.org') > 0 and
            self.messageBody.find('test comments') > 0
        )

        # until we turn off the showAll flag
        mailer.showAll = False
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            self.messageBody.find('test subject') > 0 and
            self.messageBody.find('test@test.org') < 0 and
            self.messageBody.find('test comments') > 0
        )

        # check includeEmpties
        mailer.includeEmpties = False

        # first see if everything's still included
        mailer.showAll = True
        self.messageText = ''
        mailer.onSuccess(request.form, request)
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
        request = self.LoadRequestForm(
            topic='test subject', replyto='test@test.org',)
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            self.messageBody.find('Subject') > 0
        )
        self.assertTrue(
            self.messageBody.find('Your E-Mail Address') > 0
        )
        self.assertEqual(self.messageBody.find('Comments'), -1)

    def test_ccOverride(self):
        """ Test override for CC field """

        mailer = get_actions(self.ff1)['mailer']
        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        mailer.cc_recipients = 'test@testme.com'
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            'test@testme.com' in self.mto
        )

        # simple override
        mailer.ccOverride = 'string:test@testme.com'
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            'test@testme.com' in self.mto
        )

        # list override
        mailer.ccOverride = "python:['test@testme.com', 'test1@testme.com']"
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            'test@testme.com' in self.mto and
            'test1@testme.com' in self.mto
        )

    def test_bccOverride(self):
        """ Test override for BCC field """
        mailer = get_actions(self.ff1)['mailer']
        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        mailer.bcc_recipients = 'test@testme.com'
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            'test@testme.com' in self.mto
        )

        # simple override
        mailer.bccOverride = 'string:test@testme.com'
        self.messageText = ''
        mailer.onSuccess(request.form, request)
        self.assertTrue(
            'test@testme.com' in self.mto
        )

        # list override
        mailer.bccOverride = "python:['test@testme.com', 'test1@testme.com']"
        self.messageText = ''
        mailer.onSuccess(request.form, request)
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

        request = self.LoadRequestForm(
            topic='test subject',
            replyto='test@test.org',
            comments='test comments'
        )

        self.messageText = ''
        with self.assertRaises(Exception) as context:
            mailer.onSuccess(request.form, request)
        self.assertTrue(
            isinstance(context.exception, ValueError)
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFunctions))
    return suite
