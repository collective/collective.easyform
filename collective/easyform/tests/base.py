# -*- coding: utf-8 -*-
from Products.MailHost.MailHost import MailHost
from Products.MailHost.interfaces import IMailHost
from Testing.ZopeTestCase import FunctionalTestCase
from email import message_from_string
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import Layer
from plone.testing.z2 import Browser
from plone.testing.z2 import ZSERVER_FIXTURE
from transaction import commit
from unittest2 import TestCase
from zope.component import getSiteManager


class MailHostMock(MailHost):

    def _send(self, mfrom, mto, messageText, immediate=False):
        print '<sent mail from {0} to {1}>'.format(mfrom, mto)
        self.msgtext = messageText
        self.msg = message_from_string(messageText.lstrip())


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        try:
            import plone.app.contenttypes
            import plone.app.dexterity
            self.loadZCML(
                package=plone.app.dexterity, context=configurationContext)
            self.loadZCML(
                package=plone.app.contenttypes, context=configurationContext)
        except ImportError:
            pass

        import collective.easyform
        self.loadZCML(
            package=collective.easyform, context=configurationContext)
        try:
            import plone.formwidget.recaptcha
            self.loadZCML(
                package=plone.formwidget.recaptcha, context=configurationContext)
        except ImportError:
            pass

    def setUpPloneSite(self, portal):
        try:
            self.applyProfile(portal, 'plone.app.contenttypes:default')
        except:
            pass

        # Install the collective.easyform product
        self.applyProfile(portal, 'collective.easyform:default')
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.manage_changeProperties(
            **{'email_from_address': 'mdummy@address.com'})


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


class EasyFormFunctionalTestCase(FunctionalTestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal.invokeFactory('Folder', 'news')
        self.browser = Browser(self.app)
        self.browser.addHeader('Authorization', 'Basic admin:secret')
        self.anon_browser = Browser(self.app)
        self.portal_url = 'http://nohost/plone'
        self.afterSetUp()
        commit()

    def afterSetUp(self):
        self.portal.MailHost = mailhost = MailHostMock()
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

    def setStatusCode(self, key, value):
        from ZPublisher import HTTPResponse
        HTTPResponse.status_codes[key.lower()] = value
