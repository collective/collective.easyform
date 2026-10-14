#
# Integration tests specific to the Double Opt-In action
#
from collective.easyform.actions import doubleoptin_peek
from collective.easyform.actions import get_doubleoptin_store
from collective.easyform.api import get_actions
from collective.easyform.tests import base
from datetime import timedelta
from email import message_from_bytes
from plone import api

import re

FIELDS_MODEL = """
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="name" type="zope.schema.TextLine">
      <title>Name</title>
    </field>
    <field name="email" type="zope.schema.TextLine">
      <title>E-Mail</title>
    </field>
  </schema>
</model>
"""

ACTIONS_MODEL = """
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="doubleoptin" type="collective.easyform.actions.DoubleOptIn">
      <title>Double Opt-In</title>
      <email_field>email</email_field>
      <expiry_hours>48</expiry_hours>
    </field>
    <field name="mailer" type="collective.easyform.actions.Mailer">
      <title>Mailer</title>
      <recipient_email>mdummy@address.com</recipient_email>
      <msg_subject>New submission</msg_subject>
    </field>
    <field name="saver" type="collective.easyform.actions.SaveData">
      <title>Save Data</title>
    </field>
  </schema>
</model>
"""

# same actions, Double Opt-In added last - as it happens when an editor adds it
# to an existing form
ACTIONS_MODEL_DOUBLEOPTIN_LAST = """
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="mailer" type="collective.easyform.actions.Mailer">
      <title>Mailer</title>
      <recipient_email>mdummy@address.com</recipient_email>
      <msg_subject>New submission</msg_subject>
    </field>
    <field name="saver" type="collective.easyform.actions.SaveData">
      <title>Save Data</title>
    </field>
    <field name="doubleoptin" type="collective.easyform.actions.DoubleOptIn">
      <title>Double Opt-In</title>
      <email_field>email</email_field>
    </field>
  </schema>
</model>
"""

SUBMITTER = "submitter@example.org"


class DoubleOptInTests(base.EasyFormTestCase):
    """Test the Double Opt-In action"""

    def collect_send(self, mfrom, mto, messageText, immediate=False):
        if hasattr(messageText, "encode"):
            messageText = messageText.encode("utf-8")
        self.messages.append((mfrom, mto, messageText))

    def afterSetUp(self):
        super().afterSetUp()
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.ff1.CSRFProtection = False  # no csrf protection
        self.ff1.fields_model = FIELDS_MODEL
        self.ff1.actions_model = ACTIONS_MODEL
        self.messages = []
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.collect_send
        self.request = self.layer["request"]
        api.portal.set_registry_record("plone.email_from_address", "mdummy@address.com")

    def submit(self, **values):
        self.request.form.clear()
        for key, value in values.items():
            self.request.form["form.widgets." + key] = value
        self.request.form["form.buttons.submit"] = "Submit"
        self.request.method = "POST"
        self.request.environ["REQUEST_METHOD"] = "POST"
        view = self.ff1.restrictedTraverse("@@view")
        view.update()
        return view

    def body_of(self, index):
        """Decoded body of the n-th sent mail (text bodies are
        quoted-printable encoded, the raw text cannot be searched)"""
        message = message_from_bytes(self.messages[index][2])
        return message.get_payload(decode=True).decode("utf-8")

    def token_from_mail(self):
        match = re.search(r"token=([A-Za-z0-9_-]+)", self.body_of(0))
        self.assertIsNotNone(match, "confirmation mail carries no token")
        return match.group(1)

    def confirm(self, token, method="POST"):
        self.request.form.clear()
        self.request.form["token"] = token
        self.request.method = method
        self.request.environ["REQUEST_METHOD"] = method
        view = self.ff1.restrictedTraverse("@@doubleoptin-confirm")
        html = view()
        return view, html

    def test_submit_sends_confirmation_only(self):
        self.submit(name="Maria Muster", email=SUBMITTER)

        location = self.request.response.getHeader("Location")
        self.assertTrue(location.endswith("/ff1/@@doubleoptin-pending"), location)

        self.assertEqual(len(self.messages), 1, "only the confirmation mail is sent")
        self.assertEqual(self.messages[0][1], [SUBMITTER])
        self.assertIn("/ff1/@@doubleoptin-confirm?token=", self.body_of(0))
        self.assertIn(self.ff1.Title(), self.body_of(0))

        store = get_doubleoptin_store(self.ff1)
        self.assertEqual(len(store), 1)
        entry = list(store.values())[0]
        self.assertEqual(entry["email"], SUBMITTER)
        self.assertEqual(entry["data"]["name"], "Maria Muster")

        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0, "Save Data must wait for confirmation")

    def test_confirmation_replays_other_actions(self):
        self.submit(name="Maria Muster", email=SUBMITTER)
        token = self.token_from_mail()
        self.messages = []

        # GET only asks for the click, nothing is consumed yet
        view, html = self.confirm(token, method="GET")
        self.assertEqual(view.status, "ask")
        self.assertIn(token, html)
        self.assertEqual(len(get_doubleoptin_store(self.ff1)), 1)
        self.assertEqual(self.messages, [])

        view, html = self.confirm(token)
        self.assertEqual(view.status, "confirmed")
        self.assertIn(self.ff1.thankstitle, html)

        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0][1], ["mdummy@address.com"])
        self.assertIn("Maria Muster", self.body_of(0))

        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver.getSavedFormInput()[0]["email"], SUBMITTER)
        self.assertEqual(len(get_doubleoptin_store(self.ff1)), 0)

        # a token works exactly once
        view, html = self.confirm(token)
        self.assertEqual(view.status, "invalid")
        self.assertEqual(len(self.messages), 1)

    def test_position_of_the_action_does_not_matter(self):
        self.ff1.actions_model = ACTIONS_MODEL_DOUBLEOPTIN_LAST
        self.submit(name="Maria Muster", email=SUBMITTER)

        self.assertEqual(len(self.messages), 1, "only the confirmation mail is sent")
        self.assertEqual(self.messages[0][1], [SUBMITTER])
        self.assertEqual(get_actions(self.ff1)["saver"].itemsSaved(), 0)
        self.assertEqual(len(get_doubleoptin_store(self.ff1)), 1)

        token = self.token_from_mail()
        self.messages = []
        view, html = self.confirm(token)
        self.assertEqual(view.status, "confirmed")
        self.assertEqual(self.messages[0][1], ["mdummy@address.com"])
        self.assertEqual(get_actions(self.ff1)["saver"].itemsSaved(), 1)

    def test_disabled_action_holds_nothing_back(self):
        actions = get_actions(self.ff1)
        actions["doubleoptin"].required = False
        from collective.easyform.api import set_actions

        set_actions(self.ff1, actions)
        self.submit(name="Maria Muster", email=SUBMITTER)

        self.assertEqual(self.messages[0][1], ["mdummy@address.com"])
        self.assertEqual(get_actions(self.ff1)["saver"].itemsSaved(), 1)
        self.assertEqual(len(get_doubleoptin_store(self.ff1)), 0)

    def test_confirmation_honours_thanks_page_redirect(self):
        self.ff1.thanksPageOverrideAction = "redirect_to"
        self.ff1.thanksPageOverride = "string:${portal_url}/thank-you"
        self.submit(name="Maria Muster", email=SUBMITTER)
        token = self.token_from_mail()

        view, html = self.confirm(token)
        self.assertEqual(view.status, "confirmed")
        self.assertEqual(html, "")
        self.assertTrue(
            self.request.response.getHeader("Location").endswith("/plone/thank-you")
        )

    def test_expired_token_is_rejected(self):
        self.submit(name="Maria Muster", email=SUBMITTER)
        token = self.token_from_mail()
        self.messages = []
        store = get_doubleoptin_store(self.ff1)
        store[token]["created"] -= timedelta(hours=49)

        self.assertIsNone(doubleoptin_peek(self.ff1, token))
        view, html = self.confirm(token)
        self.assertEqual(view.status, "invalid")
        self.assertEqual(self.messages, [])
        self.assertEqual(len(store), 0)
        self.assertEqual(get_actions(self.ff1)["saver"].itemsSaved(), 0)

    def test_unknown_token_is_rejected(self):
        view, html = self.confirm("does-not-exist", method="GET")
        self.assertEqual(view.status, "invalid")
        view, html = self.confirm("does-not-exist")
        self.assertEqual(view.status, "invalid")

    def test_invalid_email_is_a_field_error(self):
        action = get_actions(self.ff1)["doubleoptin"]
        errors = action.onSuccess({"name": "x", "email": "no-mail"}, self.request)
        self.assertEqual(list(errors), ["email"])
        self.assertEqual(self.messages, [])
        self.assertEqual(len(get_doubleoptin_store(self.ff1)), 0)

    def test_pending_page_shows_action_texts(self):
        html = self.ff1.restrictedTraverse("@@doubleoptin-pending")()
        self.assertIn("Please confirm your e-mail address", html)
        self.assertIn("confirmation link", html)
