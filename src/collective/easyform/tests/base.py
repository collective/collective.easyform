# -*- coding: utf-8 -*-
from email import message_from_string
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import Layer
from plone.testing.z2 import ZSERVER_FIXTURE
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost
from unittest import TestCase
from zope.component import getSiteManager


class MailHostMock(MailHost):

    def _send(self, mfrom, mto, messageText, immediate=False):
        print('<sent mail from {0} to {1}>'.format(mfrom, mto))  # noqa: T003
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

    def setUpPloneSite(self, portal):
        # Install the collective.easyform product
        self.applyProfile(portal, 'collective.easyform:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.manage_changeProperties(
            email_from_address='mdummy@address.com')
        portal.MailHost = mailhost = MailHostMock()
        sm = getSiteManager(context=portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='collective.easyform:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='collective.easyform:Functional',
)
ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, ZSERVER_FIXTURE),
    name='collective.easyform:Acceptance')
ROBOT_TESTING = Layer(name='collective.easyform:Robot')


class EasyFormTestCase(TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.afterSetUp()

    def afterSetUp(self):
        pass


class EasyFormFunctionalTestCase(TestCase):

    layer = FUNCTIONAL_TESTING
