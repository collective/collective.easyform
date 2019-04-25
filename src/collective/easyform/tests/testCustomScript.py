# -*- coding: utf-8 -*-
"""

    Unit test for EasyForm custom scripts

    Copyright 2006 Red Innovation http://www.redinnovation.com

"""
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from App.class_init import InitializeClass
from collective.easyform.api import get_actions
from collective.easyform.tests import base
from plone.app.testing import logout
from Products.CMFCore import permissions

import six


test_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, easyform, request
##title=Succesfully working script
##

from Products.CMFCore.utils import getToolByName

assert fields['test_field'] == '123'
return 'foo'
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
##parameters=fields, easyform, request
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
##parameters=fields, easyform
##title=
##
return 'asdfaf' + 1
"""

security_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, easyform, request
##title=Script needing special privileges
##

from Products.CMFCore.utils import getToolByName

portal_url = getToolByName(context, 'portal_url')
portal = portal_url.getPortalObject()

print(portal)

# Try set left_slots
portal.manage_addProperty('foo', ['foo'], 'lines')
"""

proxied_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, easyform, request
##title=Script needing special privileges
##

# Should raise Unauthorized
return request.fooProtected()
"""

return_error_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, easyform, request
##title=
##
return {'comments': 'Please enter more text'}
"""

default_params_script = """
fields
easyform
request
"""


class FakeRequest(dict):
    def __init__(self, **kwargs):
        self.form = kwargs


class SecureFakeRequest(dict):

    security = ClassSecurityInfo()

    def __init__(self, **kwargs):
        self.form = kwargs

    @security.protected(permissions.ManagePortal)
    def fooProtected(self):
        """ Only manager can access this """
        return "foo"


InitializeClass(SecureFakeRequest)


class TestCustomScript(base.EasyFormTestCase):

    """ Test FormCustomScriptAdapter functionality in EasyForm """

    def afterSetUp(self):
        self.request = self.layer["request"]

        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.ff1.CSRFProtection = False
        self.request["form.widgets.title"] = u"Test field"
        self.request["form.widgets.__name__"] = u"test_field"
        self.request["form.widgets.description"] = u"foobar"
        self.request["form.widgets.factory"] = ["label_textline_field"]
        self.request["form.widgets.required"] = ["selected"]
        self.request["form.buttons.add"] = u"Add"
        view = self.ff1.restrictedTraverse("fields/@@add-field")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

    def createScript(self):
        """ Creates FormCustomScript object """
        # 1. Create custom script adapter in the form folder
        self.request["form.widgets.title"] = u"Adapter"
        self.request["form.widgets.__name__"] = u"adapter"
        self.request["form.widgets.description"] = u""
        self.request["form.widgets.factory"] = ["Custom Script"]
        self.request["form.buttons.add"] = u"Add"
        view = self.ff1.restrictedTraverse("actions/@@add-action")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        # 2. Check that creation succeeded
        actions = get_actions(self.ff1)
        self.assertTrue("adapter" in actions)

    def testSuccess(self):
        """ Succesful script execution

        Creates a script, some form content,
        executes form handling.
        """

        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions["adapter"]

        # 4. Set script data
        adapter.ScriptBody = test_script

        req = FakeRequest(test_field="123")

        reply = adapter.onSuccess({}, req)
        assert reply == "foo", "Script returned:" + str(reply)

    def testRunTimeError(self):
        """ Script has run-time error """
        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions["adapter"]

        # 4. Set script data
        adapter.ScriptBody = runtime_error_script

        # Execute script
        throwed = False
        try:
            reply = adapter.onSuccess({})
        except TypeError:
            reply = None
            throwed = True

        assert throwed, "Bad script didn't throw run-time exception, got " + str(reply)
        assert reply is None

    def testSyntaxError(self):
        """ Script has syntax errors

        TODO: Syntax errors are not returned in validation?
        """

        # Note: this test logs an error message; it does not indicate test
        # failure

        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions["adapter"]

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
        adapter = actions["adapter"]

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
        adapter = actions["adapter"]

        # 4. Set script data
        adapter.ScriptBody = default_params_script

        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )

        errors = adapter.onSuccess({}, request)
        self.assertEqual(errors, None)

    def testSecurity(self):
        """ Script needing proxy role

        TODO: Why no security exceptions are raised?
        """
        self.createScript()
        logout()

        actions = get_actions(self.ff1)
        adapter = actions["adapter"]

        # 4. Set script data
        adapter.ScriptBody = security_script

        # Execute script
        throwed = False
        try:
            adapter.onSuccess({}, FakeRequest())
        except Unauthorized:
            throwed = True

        if self.portal.hasProperty("foo"):
            assert "Script executed under full priviledges"

        self.assertTrue(throwed, "Bypassed security, baaad!")

        adapter.ProxyRole = u"Manager"
        throwed = False
        try:
            adapter.onSuccess({}, FakeRequest())
        except Unauthorized:
            throwed = True

        if not self.portal.hasProperty("foo"):
            assert "Script not executed thru proxy role"
        self.assertFalse(throwed, "Unauthorized was raised!")

    def testSetProxyRole(self):
        """ Exercise setProxyRole """
        self.createScript()
        self.request["form.widgets.title"] = u"Adapter"
        self.request["form.widgets.description"] = u""
        self.request["form.widgets.ProxyRole"] = [u"Manager"]
        self.request["form.widgets.ScriptBody"] = six.text_type(proxied_script)
        self.request["form.widgets.IActionExtender.execCondition"] = u""
        self.request["form.buttons.save"] = u"Save"
        view = self.ff1.restrictedTraverse("actions")
        view = view.publishTraverse(view.request, "adapter")
        view = view.publishTraverse(view.request, "adapter")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        self.request["form.widgets.title"] = u"Adapter"
        self.request["form.widgets.description"] = u""
        self.request["form.widgets.ProxyRole"] = [u"none"]
        self.request["form.widgets.ScriptBody"] = six.text_type(proxied_script)
        self.request["form.widgets.IActionExtender.execCondition"] = u""
        self.request["form.buttons.save"] = u"Save"
        view = self.ff1.restrictedTraverse("actions")
        view = view.publishTraverse(view.request, "adapter")
        view = view.publishTraverse(view.request, "adapter")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        self.request["form.widgets.title"] = u"Adapter"
        self.request["form.widgets.description"] = u""
        self.request["form.widgets.ProxyRole"] = [u"bogus"]
        self.request["form.widgets.ScriptBody"] = six.text_type(proxied_script)
        self.request["form.widgets.IActionExtender.execCondition"] = u""
        self.request["form.buttons.save"] = u"Save"
        view = self.ff1.restrictedTraverse("actions")
        view = view.publishTraverse(view.request, "adapter")
        view = view.publishTraverse(view.request, "adapter")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].message, u"Required input is missing.")

    def testProxyRole(self):
        """ Test seeing how setting proxy role affects unauthorized
        Exception
        """
        self.createScript()

        actions = get_actions(self.ff1)
        adapter = actions["adapter"]

        # 4. Set script data
        adapter.ScriptBody = proxied_script

        req = SecureFakeRequest(test_field="123")
        self.assertRaises(Unauthorized, adapter.onSuccess, {}, req)
