# -*- coding: utf-8 -*-
from collective.easyform.api import get_actions
from collective.easyform.api import set_actions
from collective.easyform.tests import base
from z3c.form.interfaces import IFormLayer
from zope.interface import classImplements
from ZPublisher.BaseRequest import BaseRequest

import transaction


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


class TestEmbedding(base.EasyFormTestCase):

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
        base.EasyFormTestCase.afterSetUp(self)
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.ff1.title = u"ff1"
        self.ff1.CSRFProtection = False  # no csrf protection
        actions = get_actions(self.ff1)
        actions["mailer"].recipient_email = u"mdummy@address.com"
        set_actions(self.ff1, actions)
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        classImplements(BaseRequest, IFormLayer)

    def test_embedded_form_renders(self):
        view = self.ff1.restrictedTraverse("@@embedded")
        res = view()

        # form renders
        self.assertTrue("Your E-Mail Address" in res)

        # form action equals request URL
        self.assertTrue('action="{url}"'.format(url=self.ff1.absolute_url()) in res)

        # no form prefix
        # self.assertTrue('name="form.submitted"' in res)

        # we can specify a form prefix
        view.prefix = "mypfg"
        res = view()
        self.assertTrue('name="mypfg.buttons.submit"' in res)

    def test_embedded_form_validates(self):
        # fake an incomplete form submission
        self.LoadRequestForm(**{"mypfg.buttons.submit": u"Submit"})

        # render the form
        view = self.ff1.restrictedTraverse("@@embedded")
        view.prefix = "mypfg"
        res = view()

        # should stay on same page on errors, and show messages
        self.assertTrue("Required input is missing." in res)

    def test_doesnt_process_submission_of_other_form(self):
        # fake submission of a *different* form (note mismatch of form
        # submission marker with prefix)
        self.LoadRequestForm(**{"form.buttons.submit": u"Submit"})

        # let's preset a faux controller_state (as if from the other form)
        # to make sure it doesn't throw things off
        # self.app.REQUEST.set('controller_state', 'foobar')

        # render the form
        view = self.ff1.restrictedTraverse("@@embedded")
        view.prefix = "mypfg"
        res = view()

        # should be no validation errors
        self.assertFalse("Required input is missing." in res)

        # (and request should still have the 'form.submitted' key)
        # self.assertTrue('form.submitted' in self.app.REQUEST.form)

        # (and the controller state should be untouched)
        # self.assertEqual(self.app.REQUEST.get('controller_state'), 'foobar')

        # but if we remove the form prefix then it should process the form
        view.prefix = "form"
        res = view()
        self.assertTrue("Required input is missing." in res)

    def test_render_thank_you_on_success(self):
        # We need to be able to make sure the transaction commit was called
        # before the Retry exception, without actually committing our test
        # fixtures.
        real_transaction_commit = transaction.commit
        transaction.commit = TrueOnceCalled()
        # committed = TrueOnceCalled()

        self.LoadRequestForm(
            **{
                "form.widgets.topic": u"monkeys",
                "form.widgets.comments": u"I am not a walnut.",
                "form.widgets.replyto": u"foobar@example.com",
                "form.buttons.submit": u"Submit",
            }
        )
        # should raise a retry exception triggering a new publish attempt
        # with the new URL
        # XXX do a full publish for this test
        self.app.REQUEST._orig_env["PATH_TRANSLATED"] = "/plone"
        self.app.REQUEST.method = "POST"
        view = self.ff1.restrictedTraverse("@@embedded")
        # self.assertRaises(Retry, view)
        res = view()

        self.assertTrue("Thanks for your input." in res)

        # make sure the transaction was committed
        # XXX fails in python 3
        # self.assertTrue(committed)

        # make sure it can deal with VHM URLs
        self.app.REQUEST._orig_env[
            "PATH_TRANSLATED"
        ] = "/VirtualHostBase/http/nohost:80/VirtualHostRoot"
        view = self.ff1.restrictedTraverse("@@embedded")
        res = view()

        self.assertTrue("Thanks for your input." in res)
        # clean up
        transaction.commit = real_transaction_commit
