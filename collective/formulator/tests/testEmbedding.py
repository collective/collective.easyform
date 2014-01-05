#import os
#import sys

# if __name__ == '__main__':
    #execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.interface import classImplements
from z3c.form.interfaces import IFormLayer
from ZPublisher.BaseRequest import BaseRequest
from collective.formulator.tests import pfgtc

import transaction
#from ZPublisher.Publish import Retry


class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs


class TrueOnceCalled(object):

    """ A mock function that evaluates to True once it has been called. """

    def __init__(self):
        self.called = False

    def __call__(self, *args, **kw):
        self.called = True

    def __bool__(self):
        return self.called


class TestEmbedding(pfgtc.PloneFormGenTestCase):

    """ test embedding of a PFG in another template """

    def dummy_send(self, mfrom, mto, messageText, immediate=False):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText

    def LoadRequestForm(self, **kwargs):
        form = self.app.REQUEST.form
        form.clear()
        for key in kwargs.keys():
            form[key] = kwargs[key]
        return self.app.REQUEST

    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)
        self.folder.invokeFactory('Formulator', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.title = u"ff1"
        self.ff1.checkAuthenticator = False  # no csrf protection
        self.ff1.actions_model = (
            self.ff1.actions_model.replace(
                u"<description>E-Mails Form Input</description>",
                u"<recipient_email>mdummy@address.com</recipient_email><description>E-Mails Form Input</description>"))
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        self.portal.manage_changeProperties(
            **{'email_from_address': 'mdummy@address.com'})
        classImplements(BaseRequest, IFormLayer)

    def test_embedded_form_renders(self):
        view = self.ff1.restrictedTraverse('@@embedded')
        res = view()

        # form renders
        self.assertTrue('Your E-Mail Address' in res)

        # form action equals request URL
        self.assertTrue('action="%s"' % self.ff1.absolute_url() in res)

        # no form prefix
        #self.assertTrue('name="form.submitted"' in res)

        # we can specify a form prefix
        view.prefix = 'mypfg'
        res = view()
        self.assertTrue('name="mypfg.buttons.save"' in res)

    def test_embedded_form_validates(self):
        # fake an incomplete form submission
        self.LoadRequestForm(**{
            'mypfg.buttons.save': u'Submit',
        })

        # render the form
        view = self.ff1.restrictedTraverse('@@embedded')
        view.prefix = 'mypfg'
        res = view()

        # should stay on same page on errors, and show messages
        self.assertTrue('Required input is missing.' in res)

    def test_doesnt_process_submission_of_other_form(self):
        # fake submission of a *different* form (note mismatch of form
        # submission marker with prefix)
        self.LoadRequestForm(**{
            'form.buttons.save': u'Submit',
        })

        # let's preset a faux controller_state (as if from the other form)
        # to make sure it doesn't throw things off
        #self.app.REQUEST.set('controller_state', 'foobar')

        # render the form
        view = self.ff1.restrictedTraverse('@@embedded')
        view.prefix = 'mypfg'
        res = view()

        # should be no validation errors
        self.assertFalse('Required input is missing.' in res)

        # (and request should still have the 'form.submitted' key)
        #self.assertTrue('form.submitted' in self.app.REQUEST.form)

        # (and the controller state should be untouched)
        #self.assertEqual(self.app.REQUEST.get('controller_state'), 'foobar')

        # but if we remove the form prefix then it should process the form
        view.prefix = 'form'
        res = view()
        self.assertTrue('Required input is missing.' in res)

    def test_render_thank_you_on_success(self):
        # We need to be able to make sure the transaction commit was called
        # before the Retry exception, without actually committing our test
        # fixtures.
        real_transaction_commit = transaction.commit
        transaction.commit = committed = TrueOnceCalled()

        self.LoadRequestForm(**{
            'form.widgets.topic': u'monkeys',
            'form.widgets.comments': u'I am not a walnut.',
            'form.widgets.replyto': u'foobar@example.com',
            'form.buttons.save': u'Submit',
        })
        # should raise a retry exception triggering a new publish attempt
        # with the new URL
        # XXX do a full publish for this test
        self.app.REQUEST._orig_env['PATH_TRANSLATED'] = '/plone'
        view = self.ff1.restrictedTraverse('@@embedded')
        #self.assertRaises(Retry, view)
        res = view()

        self.assertTrue('Thank You' in res)
        self.assertTrue('Thanks for your input.' in res)

        # self.assertEqual(self.app.REQUEST._orig_env['PATH_INFO'],
                         #'/plone/Members/test_user_1_/ff1/thank-you')

        # make sure the transaction was committed
        self.assertTrue(committed)

        # make sure it can deal with VHM URLs
        self.app.REQUEST._orig_env[
            'PATH_TRANSLATED'] = '/VirtualHostBase/http/nohost:80/VirtualHostRoot'
        view = self.ff1.restrictedTraverse('@@embedded')
        res = view()

        self.assertTrue('Thank You' in res)
        self.assertTrue('Thanks for your input.' in res)
        #self.assertRaises(Retry, view)
        # self.assertEqual(self.app.REQUEST._orig_env['PATH_INFO'],
                         #'/VirtualHostBase/http/nohost:80/VirtualHostRoot/plone/Members/test_user_1_/ff1/thank-you')

        # clean up
        transaction.commit = real_transaction_commit


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEmbedding))
    return suite
