# -*- coding: utf-8 -*-
#
# Integration tests specific to save-data adapter.
#

from AccessControl.unauthorized import Unauthorized
from collective.easyform.api import get_actions
from collective.easyform.api import get_schema
from collective.easyform.interfaces import ISaveData
from collective.easyform.tests import base
from os.path import dirname
from os.path import join
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser
from six import BytesIO
from six.moves import zip
from transaction import commit
from zExceptions.unauthorized import Unauthorized as zUnauthorized
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

import plone.protect
import sys
import transaction
import unittest

try:
    from openpyxl import load_workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def FakeRequest(method="GET", add_auth=False, **kwargs):
    environ = {}
    environ.setdefault("SERVER_NAME", "foo")
    environ.setdefault("SERVER_PORT", "80")
    environ.setdefault("REQUEST_METHOD", method)
    if api.env.plone_version() < "5.2":
        # manually set stdout for Plone < 5.2
        request = HTTPRequest(sys.stdin, environ, HTTPResponse(stdout=BytesIO()))
    else:
        request = HTTPRequest(sys.stdin, environ, HTTPResponse())
    request.form = kwargs
    if add_auth:
        request.form["_authenticator"] = plone.protect.createToken()
    return request


class BaseSaveData(base.EasyFormTestCase):

    """test save data adapter"""

    def setUp(self):
        base.EasyFormTestCase.setUp(self)
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")

    def createSaver(self):
        """Creates FormCustomScript object"""
        # 1. Create custom script adapter in the form folder
        self.portal.REQUEST["form.widgets.title"] = u"Saver"
        self.portal.REQUEST["form.widgets.__name__"] = u"saver"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.factory"] = ["Save Data"]
        self.portal.REQUEST["form.buttons.add"] = u"Add"
        view = self.ff1.restrictedTraverse("actions/@@add-action")
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        # 2. Check that creation succeeded
        actions = get_actions(self.ff1)
        self.assertTrue("saver" in actions)


class SaveDataTestCase(BaseSaveData):

    def testSavedDataView(self):
        """test saved data view"""

        self.createSaver()

        view = self.ff1.restrictedTraverse("saveddata")
        self.assertEqual(list(view.items()), [("saver", u"Saver")])

        # as the owner, TEST_USER_ID can still see the saved data
        setRoles(self.portal, TEST_USER_ID, [])
        view = self.ff1.restrictedTraverse("saveddata")
        self.assertIsNotNone(view)
        logout()

        # other editors / reviewers / ... don't have access to the saved data
        api.user.create(email="test@plone.org", username="test")
        setRoles(
            self.portal, "test", roles=["Reader", "Contributor", "Editor", "Reviewer"]
        )
        login(self.portal, "test")
        with self.assertRaises(Unauthorized):
            view = self.ff1.restrictedTraverse("saveddata")

    def testSaverDataFormExtraData(self):
        """test saver data form extra data"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        saver.ExtraData = ("dt",)
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, "saver")
        view = view.publishTraverse(view.request, "data")
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {"items": 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]["id"], item[0])
        self.assertEqual(item[1]["topic"], "test subject")
        self.assertEqual(item[1]["replyto"], "test@test.org")
        self.assertEqual(item[1]["comments"], "test comments")
        self.assertTrue(" " in item[1]["dt"])

    def testSaverDataFormShowFields(self):
        """test saver data form show fields"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        saver.showFields = ("topic", "comments")
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, "saver")
        view = view.publishTraverse(view.request, "data")
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {"items": 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]["id"], item[0])
        self.assertEqual(item[1]["topic"], "test subject")
        self.assertEqual(item[1]["comments"], "test comments")
        self.assertTrue("replyto" not in item[1])

    def testSaverDataFormOneItem(self):
        """test saver data form one item"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic="test subject", replyto="test@test.org", comments="test comments"
        )
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, "saver")
        view = view.publishTraverse(view.request, "data")
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {"items": 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]["id"], item[0])
        self.assertEqual(item[1]["topic"], "test subject")
        self.assertEqual(item[1]["replyto"], "test@test.org")
        self.assertEqual(item[1]["comments"], "test comments")

    def testSaverDataForm(self):
        """test saver data form"""

        self.createSaver()

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, "saver")
        view = view.publishTraverse(view.request, "data")
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {"items": 0})
        self.assertEqual([i for i in form.get_items()], [])

    def testSaver(self):
        """test save data adapter action"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        self.assertEqual(saver.itemsSaved(), 0)

        res = saver.getSavedFormInputForEdit()
        self.assertEqual(res, "")

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)

        res = saver.getSavedFormInputForEdit()
        self.assertEqual(res.strip(), "test@test.org,test subject,test comments")

    def testSaverExtraData(self):
        """test save data adapter action"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.ExtraData = ("dt",)
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        self.assertTrue("dt" in saver.getSavedFormInput()[0])

    def testSaverDownload(self):
        """test save data"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.download(request.response, delimiter=",")
        res = request.response.stdout.getvalue().decode("utf-8")
        self.assertTrue("Content-Type: text/comma-separated-values" in res)
        self.assertTrue('Content-Disposition: attachment; filename="saver.csv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit() in res)

    def testSaverDownloadTSV(self):
        """test save data"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.DownloadFormat = "tsv"
        saver.download(request.response)
        res = request.response.stdout.getvalue().decode("utf-8")
        self.assertTrue("Content-Type: text/tab-separated-values" in res)
        self.assertTrue('Content-Disposition: attachment; filename="saver.tsv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit(delimiter="\t") in res)

    @unittest.skipUnless(HAS_OPENPYXL, "Requires openpyxl")
    def testSaverDownloadXLSX(self):
        """test save data"""

        with open(join(dirname(__file__), "fixtures", "fieldset_multiple_choice.xml")) as f:
            self.ff1.fields_model = f.read()

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
            multiplechoice=["Red", "Blue"]
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.DownloadFormat = "xlsx"
        saver.download(request.response)
        res = request.response.stdout
        self.assertEqual(
            request.response.headers["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            request.response.headers["content-disposition"],
            'attachment; filename="saver.xlsx"',
        )

        wb = load_workbook(res)
        wb.active
        ws = wb.active
        rows = list(ws.rows)

        self.assertEqual(len(rows), 2)  # Row 1 is the header row
        self.assertEqual(rows[1][0].value, "test@test.org")
        self.assertEqual(rows[1][1].value, "test subject")
        self.assertEqual(rows[1][2].value, "test comments")
        self.assertEqual(rows[1][3].value, "Red|Blue")

    def testSaverDownloadWithTitles(self):
        """test save data"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.UseColumnNames = True
        saver.download(request.response, delimiter=",")
        res = request.response.stdout.getvalue().decode("utf-8")
        self.assertTrue("Content-Type: text/comma-separated-values" in res)
        self.assertTrue('Content-Disposition: attachment; filename="saver.csv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit(header=True) in res)

    def testSaverDownloadExtraData(self):
        """test save data"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.ExtraData = ("dt", "HTTP_USER_AGENT")
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.download(request.response, delimiter=",")
        res = request.response.stdout.getvalue().decode("utf-8")
        self.assertTrue("Content-Type: text/comma-separated-values" in res)
        self.assertTrue('Content-Disposition: attachment; filename="saver.csv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit() in res)

    def testSaverSavedFormInput(self):
        """test save data adapter action and direct access to
        SavedFormInput"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        row = next(iter(saver.getSavedFormInput()))
        self.assertEqual(len(row), 4)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)
        self.assertEqual(saver.itemsSaved(), 2)

        saver.clearSavedFormInput()
        self.assertEqual(saver.itemsSaved(), 0)

    def testSetSavedFormInput(self):
        """test setSavedFormInput functionality"""

        # set up saver
        self.createSaver()
        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        self.assertEqual(saver.getSavedFormInputForEdit(), "")

        # save a row
        fields = list(get_schema(self.ff1))
        saver.addDataRow(dict(list(zip(fields, ["one", "two", "three"]))))
        self.assertEqual(saver.itemsSaved(), 1)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1],
            dict(list(zip(["id"] + fields, [items[0][0], "one", "two", "three"]))),
        )
        for number in ["one", "two", "three"]:
            self.assertIn(number, saver.getSavedFormInputForEdit())

        # save a couple of \n-delimited rows - \n eol
        saver.addDataRow(dict(list(zip(fields, ["four", "five", "six"]))))
        self.assertEqual(saver.itemsSaved(), 2)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1],
            dict(list(zip(["id"] + fields, [items[0][0], "one", "two", "three"]))),
        )
        self.assertEqual(
            items[1][1],
            dict(list(zip(["id"] + fields, [items[1][0], "four", "five", "six"]))),
        )

        # order can change in py2
        for number in ["one", "two", "three", "four", "five", "six"]:
            self.assertIn(number, saver.getSavedFormInputForEdit())

        # save empty string
        saver.clearSavedFormInput()
        self.assertEqual(saver.itemsSaved(), 0)
        self.assertEqual(saver.getSavedFormInputForEdit(), "")

    def testEditSavedFormInput(self):
        """test manage_saveData functionality"""

        # set up saver
        self.createSaver()
        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        # save a row
        fields = list(get_schema(self.ff1))
        # saver.savedFormInput = 'one,two,three'
        saver.addDataRow(dict(list(zip(fields, ["one", "two", "three"]))))
        self.assertEqual(saver.itemsSaved(), 1)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1],
            dict(list(zip(["id"] + fields, [items[0][0], "one", "two", "three"]))),
        )

    def testDeleteSavedFormInput(self):
        """test manage_deleteData functionality"""

        # set up saver
        self.createSaver()
        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        # save a few rows
        fields = list(get_schema(self.ff1))
        saver.addDataRow(dict(list(zip(fields, ["one", "two", "three"]))))
        saver.addDataRow(dict(list(zip(fields, ["four", "five", "six"]))))
        saver.addDataRow(dict(list(zip(fields, ["seven", "eight", "nine"]))))
        self.assertEqual(saver.itemsSaved(), 3)

        # saver.manage_deleteData(saver._storage.keys()[1])
        saver.delDataRow(saver.getSavedFormInputItems()[1][0])
        self.assertEqual(saver.itemsSaved(), 2)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1],
            dict(list(zip(["id"] + fields, [items[0][0], "one", "two", "three"]))),
        )
        self.assertEqual(
            items[1][1],
            dict(list(zip(["id"] + fields, [items[1][0], "seven", "eight", "nine"]))),
        )

    def testSaverInputAsDictionaries(self):
        """test save data adapter's InputAsDictionaries"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        # self.ff1.setActionAdapter(('saver',))

        # self.assertEqual(saver.inputAsDictionaries,
        # saver.InputAsDictionaries)

        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)
        # errors = self.ff1.fgvalidate(REQUEST=request)
        # self.assertEqual(errors, {})

        self.assertEqual(saver.itemsSaved(), 1)

        iad = saver.getSavedFormInput()
        row = next(iter(iad))
        self.assertEqual(len(row), 4)
        self.assertEqual(row["topic"], "test subject")

    def testSaverColumnNames(self):
        """test save data adapter's getColumnNames function"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        cn = saver.getColumnNames()
        self.assertTrue(len(cn) == 3)
        self.assertTrue(cn[0] == "replyto")
        self.assertTrue(cn[1] == "topic")
        self.assertTrue(cn[2] == "comments")

        # Use selective field saving
        saver.showFields = ("topic", "comments")
        cn = saver.getColumnNames()
        self.assertTrue(len(cn) == 2)
        self.assertTrue(cn[0] == "topic")
        self.assertTrue(cn[1] == "comments")
        saver.showFields = tuple()

        # Add an extra column
        saver.ExtraData = ("dt",)
        cn = saver.getColumnNames()
        self.assertTrue(len(cn) == 4)
        self.assertTrue(cn[3] == "dt")

    def testSaverColumnTitles(self):
        """test save data adapter's getColumnTitles function"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]

        cn = saver.getColumnTitles()
        self.assertTrue(len(cn) == 3)
        self.assertTrue(cn[0] == "Your E-Mail Address")
        self.assertTrue(cn[1] == "Subject")
        self.assertTrue(cn[2] == "Comments")

        # Add an extra column
        saver.ExtraData = ("dt",)
        cn = saver.getColumnTitles()
        self.assertTrue(len(cn) == 4)
        self.assertTrue(cn[3] == "Posting Date/Time")

    def testSaverSelectiveFieldSaving(self):
        """Test selective inclusion of fields in the data"""

        self.createSaver()

        self.assertTrue("saver" in get_actions(self.ff1))
        saver = get_actions(self.ff1)["saver"]
        saver.showFields = ("topic", "comments")

        request = FakeRequest(
            add_auth=True,
            method="POST",
            topic="test subject",
            replyto="test@test.org",
            comments="test comments",
        )
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        row = next(iter(saver.getSavedFormInput()))
        self.assertEqual(len(row), 3)
        self.assertEqual(row["topic"], "test subject")
        self.assertEqual(row["comments"], "test comments")

    def testGetSaveDataAdaptersView(self):
        """test the @@get_save_data_adapters view"""

        self.createSaver()

        view = self.ff1.restrictedTraverse("@@get_save_data_adapters")
        results = view()
        self.assertEqual(len(results), 1)
        saver = results[0]
        self.assertTrue(ISaveData.providedBy(saver))


class SaverIntegrationTestCase(base.EasyFormFunctionalTestCase):
    def setUp(self):
        base.EasyFormFunctionalTestCase.setUp(self)
        self.portal = self.layer["portal"]
        self.portal_url = self.layer["portal"].absolute_url()
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic " + SITE_OWNER_NAME + ":" + SITE_OWNER_PASSWORD
        )
        self.createSaver()

    def createSaver(self):
        """Creates FormCustomScript object"""
        # 1. Create custom script adapter in the form folder
        self.portal.REQUEST["form.widgets.title"] = u"Saver"
        self.portal.REQUEST["form.widgets.__name__"] = u"saver"
        self.portal.REQUEST["form.widgets.description"] = u""
        self.portal.REQUEST["form.widgets.factory"] = ["Save Data"]
        self.portal.REQUEST["form.buttons.add"] = u"Add"
        view = self.ff1.restrictedTraverse("actions/@@add-action")
        view.update()
        commit()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        # 2. Check that creation succeeded
        actions = get_actions(self.ff1)
        self.assertTrue("saver" in actions)

    def test_download_saveddata_view(self):
        self.browser.open(self.portal_url + "/test-folder/ff1/@@actions/saver/@@data")
        self.assertTrue("Saved Data" in self.browser.contents)
        self.assertTrue(
            "viewpermission-collective-easyform-download-saved-input"
            in self.browser.contents
        )

        # editors / reviewers / ... don't have access to the saved data
        api.user.create(email="test@plone.org", username="test", password="password")
        setRoles(
            self.portal, "test", roles=["Reader", "Contributor", "Editor", "Reviewer"]
        )
        self.browser.addHeader("Authorization", "Basic " + "test" + ":" + "password")
        transaction.commit()
        with self.assertRaises(zUnauthorized):
            self.browser.open(
                self.portal_url + "/test-folder/ff1/@@actions/saver/@@data"
            )

    def test_download_saveddata_suggests_csv_delimiter_default_registry_value(self):
        self.browser.open(self.portal_url + "/test-folder/ff1/@@actions/saver/@@data")
        self.assertTrue("Saved Data" in self.browser.contents)
        input = self.browser.getControl("CSV delimiter")
        self.assertEqual(input.value, ",")

    def test_download_saveddata_suggests_csv_delimiter_updated_registry_value(self):
        # 1. set custom CSV delimiter in registry
        self.browser.open(self.portal_url + "/@@easyform-controlpanel")
        input = self.browser.getControl(label="CSV delimiter")
        input.value = ";"
        self.browser.getControl("Save").click()
        # 2. tests that custom value is used
        self.browser.open(self.portal_url + "/test-folder/ff1/@@actions/saver/@@data")
        input = self.browser.getControl("CSV delimiter")
        self.assertEqual(input.value, ";")

    def test_download_saveddata_csv_delimiter_required(self):
        self.browser.open(self.portal_url + "/test-folder/ff1/@@actions/saver/@@data")
        self.assertTrue("Saved Data" in self.browser.contents)
        input = self.browser.getControl("CSV delimiter")
        input.value = ""
        self.browser.getControl(name="form.buttons.download").click()
        self.assertEqual(
            self.browser.url,
            "http://nohost/plone/test-folder/ff1/@@actions/saver/@@data",
        )
        self.assertTrue("CSV delimiter is required." in self.browser.contents)

    def test_download_saveddata_csv_delimiter_from_form(self):
        self.browser.open(
            self.portal_url + "/test-folder/ff1/@@actions/saver/@@data"
        )
        self.assertTrue("Saved Data" in self.browser.contents)
        self.browser.getControl(name="form.buttons.download").click()
        self.assertEqual(
            self.browser.contents, "Your E-Mail Address,Subject,Comments\r\n"
        )
        self.browser.open(
            self.portal_url + "/test-folder/ff1/@@actions/saver/@@data"
        )
        self.assertTrue("Saved Data" in self.browser.contents)
        input = self.browser.getControl("CSV delimiter")
        input.value = ";"
        self.browser.getControl(name="form.buttons.download").click()
        self.assertEqual(
            self.browser.contents, "Your E-Mail Address;Subject;Comments\r\n"
        )

    # this test depends on internals of zope.testbrowser controls
    def test_download_saveddata_suggests_csv_delimiter_defines_maxlength(self):
        self.browser.open(
            self.portal_url + "/test-folder/ff1/@@actions/saver/@@data"
        )
        self.assertTrue("Saved Data" in self.browser.contents)
        input = self.browser.getControl("CSV delimiter")
        self.assertTrue(input._elem.has_attr("maxlength"))
        self.assertEqual(input._elem.get("maxlength"), u"1")
