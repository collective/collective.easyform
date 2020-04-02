# -*- coding: utf-8 -*-
from __future__ import print_function
from email import message_from_string
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost
from unittest import TestCase
from zope.component import getSiteManager


try:
    from plone.testing.zope import WSGI_SERVER_FIXTURE
except ImportError:
    from plone.testing.z2 import ZSERVER_FIXTURE as WSGI_SERVER_FIXTURE


class MailHostMock(MailHost):
    def _send(self, mfrom, mto, messageText, immediate=False):
        print("<sent mail from {0} to {1}>".format(mfrom, mto))  # noqa: T003
        self.msgtext = messageText
        self.msg = message_from_string(messageText.lstrip())


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        from plone.protect import auto  # noqa

        auto.CSRF_DISABLED = True
        import collective.easyform

        self.loadZCML(package=collective.easyform)
        try:
            import plone.formwidget.recaptcha

            self.loadZCML(package=plone.formwidget.recaptcha)
        except ImportError:
            pass
        try:
            import collective.z3cform.norobots

            self.loadZCML(package=collective.z3cform.norobots)
        except ImportError:
            pass

        # set default publisher encoding for Plone 5.1
        # this is set in zope.conf via plone.recipe.zope2instance but for
        # testbrowser in doctests we have to manually set it here
        # see https://github.com/collective/collective.easyform/pull/139
        if api.env.plone_version() < "5.2":
            from Zope2.Startup.datatypes import default_zpublisher_encoding

            default_zpublisher_encoding("utf-8")

    def setUpPloneSite(self, portal):
        # Install the collective.easyform product
        self.applyProfile(portal, "collective.easyform:default")
        try:
            self.applyProfile(portal, "plone.formwidget.recaptcha:default")
        except KeyError:
            pass
        setRoles(portal, TEST_USER_ID, ["Manager"])
        portal.manage_changeProperties(email_from_address="mdummy@address.com")
        portal.MailHost = mailhost = MailHostMock()
        sm = getSiteManager(context=portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="collective.easyform:Integration"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="collective.easyform:Functional"
)
ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, WSGI_SERVER_FIXTURE),
    name="collective.easyform:Acceptance",
)


class EasyFormTestCase(TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal.invokeFactory("Folder", "test-folder")
        self.folder = self.portal["test-folder"]
        self.afterSetUp()

    def afterSetUp(self):
        pass


class EasyFormFunctionalTestCase(TestCase):

    layer = FUNCTIONAL_TESTING
