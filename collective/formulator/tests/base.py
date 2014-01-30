from Products.MailHost.MailHost import MailHost
from Products.MailHost.interfaces import IMailHost
from Testing.ZopeTestCase import FunctionalTestCase
from email import message_from_string
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from transaction import commit
from unittest2 import TestCase
from zope.component import getSiteManager


class Session(dict):

    def set(self, key, value):
        self[key] = value


class MailHostMock(MailHost):

    def _send(self, mfrom, mto, messageText, immediate=False):
        print '<sent mail from %s to %s>' % (mfrom, mto)
        self.msgtext = messageText
        self.msg = message_from_string(messageText.lstrip())


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.formulator
        self.loadZCML(
            package=collective.formulator, context=configurationContext)
        try:
            import collective.recaptcha
            self.loadZCML(
                package=collective.recaptcha, context=configurationContext)
        except ImportError:
            pass

    def setUpPloneSite(self, portal):
        # Install the collective.formulator product
        self.applyProfile(portal, 'collective.formulator:default')
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        setRoles(portal, TEST_USER_ID, ['Manager'])


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='collective.formulator:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='collective.formulator:Functional',
)


class FormulatorTestCase(TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.app.REQUEST['SESSION'] = Session()
        self.portal = self.layer['portal']
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.afterSetUp()

    def afterSetUp(self):
        pass


class FormulatorFunctionalTestCase(FunctionalTestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.app.REQUEST['SESSION'] = Session()
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
        self.portal.email_from_address = 'noreply@holokinesislibros.com'

    def setStatusCode(self, key, value):
        from ZPublisher import HTTPResponse
        HTTPResponse.status_codes[key.lower()] = value
