"""

    Unit test for PloneFormGen custom scripts

    Copyright 2006 Red Innovation http://www.redinnovation.com

"""
__author__ = 'Mikko Ohtamaa <mikko@redinnovation.com>'
__docformat__ = 'plaintext'

import os
import sys


if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

try:
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from AccessControl import ClassSecurityInfo

from collective.formulator.tests import pfgtc
from collective.formulator.api import get_actions

from Products.CMFCore import permissions

test_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=Succesfully working script
##

from Products.CMFCore.utils import getToolByName

assert fields["test_field"] == "123"
return "foo"
"""

bad_parameters_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=
##title=
##

return 'foo'
"""

syntax_error_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=
##
if:
return asdfaf
"""

runtime_error_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen
##title=
##
return "asdfaf" + 1
"""

security_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=Script needing special privileges
##

from Products.CMFCore.utils import getToolByName

portal_url = getToolByName(context, "portal_url")
portal = portal_url.getPortalObject()

# Try set left_slots
portal.manage_addProperty('foo', ['foo'], 'lines')
"""

proxied_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=Script needing special privileges
##

# Should raise Unauthorized
return request.fooProtected()
"""

default_params_script = """
fields
ploneformgen
request
"""


class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs


class SecureFakeRequest(dict):

    security = ClassSecurityInfo()

    def __init__(self, **kwargs):
        self.form = kwargs

    security.declareProtected(permissions.ManagePortal,
                              'fooProtected')

    def fooProtected(self):
        """ Only manager can access this """
        return "foo"

InitializeClass(SecureFakeRequest)


class TestCustomScript(pfgtc.PloneFormGenTestCase):

    """ Test FormCustomScriptAdapter functionality in PloneFormGen """

    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)

        self.loginAsPortalOwner()

        self.folder.invokeFactory('Formulator', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        # print self.ff1.fields_model
        #self.ff1.invokeFactory('FormStringField', 'test_field')
        self.portal.REQUEST["form.widgets.title"] = u"Test field"
        self.portal.REQUEST["form.widgets.__name__"] = u"test_field"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.factory"] = ["Text line (String)"]
        self.portal.REQUEST["form.buttons.add"] = u"Add"
        view = self.ff1.restrictedTraverse("fields/@@add-field")
        view.update()
        form = view.form_instance
        # form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

    def createScript(self):
        """ Creates FormCustomScript object """
        # 1. Create custom script adapter in the form folder
        self.portal.REQUEST["form.widgets.title"] = u"Adapter"
        self.portal.REQUEST["form.widgets.__name__"] = u"adapter"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.factory"] = ["CustomScript"]
        self.portal.REQUEST["form.buttons.add"] = u"Add"
        view = self.ff1.restrictedTraverse("actions/@@add-action")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        # 2. Check that creation succeeded
        actions = get_actions(self.ff1)
        self.failUnless('adapter' in actions)

#    def testScriptTypes(self):
#        """ Check DisplayList doesn't fire exceptions """
#        self.createScript()
#        adapter = self.ff1.adapter
#        adapter.getScriptTypeChoices()

    def testSuccess(self):
        """ Succesful script execution

        Creates a script, some form content,
        executes form handling.
        """

        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions['adapter']

        # 4. Set script data
        adapter.ScriptBody = test_script

        req = FakeRequest(test_field="123")

        reply = adapter.onSuccess({}, req)
        assert reply == "foo", "Script returned:" + str(reply)

    def testRunTimeError(self):
        """ Script has run-time error """
        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions['adapter']

        # 4. Set script data
        adapter.ScriptBody = runtime_error_script

        # Execute script
        throwed = False
        try:
            reply = adapter.onSuccess({})
        except TypeError:
            reply = None
            throwed = True

        assert throwed, "Bad script didn't throw run-time exception, got " + \
            str(reply)
        assert reply == None

    def testSyntaxError(self):
        """ Script has syntax errors

        TODO: Syntax errors are not returned in validation?
        """

        # Note: this test logs an error message; it does not indicate test
        # failure

        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions['adapter']

        # 4. Set script data
        adapter.ScriptBody = syntax_error_script

        # Execute script
        throwed = False
        try:
            adapter.onSuccess({}, FakeRequest())
        except ValueError:
            throwed = True

        assert throwed, "Bad script didn't throw run-time exception"

    def testBadParameters(self):
        """ Invalid number of script parameters """

        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions['adapter']

        # 4. Set script data
        adapter.ScriptBody = bad_parameters_script

        # Execute script
        throwed = False
        try:
            adapter.onSuccess([])
        except TypeError:
            throwed = True
        assert throwed, "Invalid parameters failed silently"

    def testDefaultParameters(self):
        """ Test to make sure the documented parameters are available """

        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions['adapter']

        # 4. Set script data
        adapter.ScriptBody = default_params_script

        request = FakeRequest(
            topic='test subject', replyto='test@test.org', comments='test comments')

        errors = adapter.onSuccess({}, request)
        self.assertEqual(errors, None)

#    def testSecurity(self):
#        """ Script needing proxy role
#
#        TODO: Why no security exceptions are raised?
#        """
# self.createScript()
#
# adapter = self.ff1.adapter
# 4. Set script data
# adapter.setScriptBody(security_script)
#
# errors = adapter.validate()
# assert len(errors) == 0, "Had errors:" + str(errors)
#
# Execute script
# throwed = False
#
# adapter.onSuccess([])
#
# if hasattr(self.portal, "foo"):
# assert "Script executed under full priviledges"
#
# self.failUnless(throwed==True, "Bypassed security, baaad!")
#
#        pass
    def testSetProxyRole(self):
        """ Exercise setProxyRole """

        self.createScript()
        self.portal.REQUEST["form.widgets.title"] = u"Adapter"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.ProxyRole"] = [u"Manager"]
        self.portal.REQUEST[
            "form.widgets.ScriptBody"] = unicode(proxied_script)
        self.portal.REQUEST["form.widgets.IActionExtender.execCondition"] = u""
        self.portal.REQUEST["form.buttons.save"] = u"Save"
        view = self.ff1.restrictedTraverse("actions")
        view = view.publishTraverse(view.request, 'adapter')
        view = view.publishTraverse(view.request, 'adapter')
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        self.portal.REQUEST["form.widgets.title"] = u"Adapter"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.ProxyRole"] = [u"No proxy role"]
        self.portal.REQUEST[
            "form.widgets.ScriptBody"] = unicode(proxied_script)
        self.portal.REQUEST["form.widgets.IActionExtender.execCondition"] = u""
        self.portal.REQUEST["form.buttons.save"] = u"Save"
        view = self.ff1.restrictedTraverse("actions")
        view = view.publishTraverse(view.request, 'adapter')
        view = view.publishTraverse(view.request, 'adapter')
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        self.portal.REQUEST["form.widgets.title"] = u"Adapter"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.ProxyRole"] = [u"bogus"]
        self.portal.REQUEST[
            "form.widgets.ScriptBody"] = unicode(proxied_script)
        self.portal.REQUEST["form.widgets.IActionExtender.execCondition"] = u""
        self.portal.REQUEST["form.buttons.save"] = u"Save"
        view = self.ff1.restrictedTraverse("actions")
        view = view.publishTraverse(view.request, 'adapter')
        view = view.publishTraverse(view.request, 'adapter')
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)


# XXX TODO: We need to find another way to test this.
#    def testProxyRole(self):
#        """ Test seeing how setting proxy role affects unauthorized exception """
#
# TODO: Zope security system kills me
#
# self.createScript()
#
# adapter = self.ff1.adapter
# 4. Set script data
# adapter.setScriptBody(proxied_script)
#
# req = SecureFakeRequest(test_field="123")
# req = req.__of__(self.portal)
#
# errors = adapter.validate()
# assert len(errors) == 0, "Had errors:" + str(errors)
#
# Execute script
# throwed = False
# try:
# adapter.onSuccess([], req)
# except Unauthorized:
# throwed=True
#
# assert throwed, "No Unauthorized was raised"
#
# self.loginAsPortalOwner()
# self.setRoles(["Manager", "Owner"])
# adapter.setProxyRole("Manager")
# self.logout()
#
#        assert adapter.onSuccess([], req) == "123"

#    def testSkinsScript(self):
#        """ Test executing script from portal_skins """
#        portal_skins = self.portal.portal_skins
#        manage_addPythonScript(portal_skins.custom, "test_skins_script")
#        test_skins_script = portal_skins.custom.test_skins_script
#
#        test_skins_script.ZPythonScript_edit("", test_script)
#        self._refreshSkinData()
#
#
#        portal_skins.custom.test_skins_script({"test_field" : "123"}, "foo", None)
# Do a dummy test call
#        self.portal.test_skins_script({"test_field" : "123"}, "foo", None)
#
#        self.createScript()
#        adapter = self.ff1.adapter
#        adapter.setScriptType("skins_script")
#        adapter.setScriptName("test_skins_script")
#
#        errors = adapter.validate()
#        assert len(errors) == 0, "Had errors:" + str(errors)
#
# Execute script
#        req = FakeRequest(test_field="123")
#        reply = adapter.onSuccess([], req)
#        assert reply == "foo", "Script returned:" + str(reply)


if __name__ == '__main__':
    framework()


def test_suite():
    from unittest import TestSuite, makeSuite
    from Products.PloneTestCase.layer import ZCMLLayer
    suite = TestSuite()
    suite.layer = ZCMLLayer
    suite.addTest(makeSuite(TestCustomScript))
    return suite
