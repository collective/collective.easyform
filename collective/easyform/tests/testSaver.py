# -*- coding: utf-8 -*-
#
# Integration tests specific to save-data adapter.
#

from StringIO import StringIO
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from collective.easyform.api import get_actions
from collective.easyform.api import get_fields
from collective.easyform.tests import base
import plone.protect
import sys


def FakeRequest(method='GET', add_auth=False, **kwargs):
    environ = {}
    environ.setdefault('SERVER_NAME', 'foo')
    environ.setdefault('SERVER_PORT', '80')
    environ.setdefault('REQUEST_METHOD', method)
    request = HTTPRequest(sys.stdin,
                          environ,
                          HTTPResponse(stdout=StringIO()))
    request.form = kwargs
    if add_auth:
        request.form['_authenticator'] = plone.protect.createToken()
    return request


class TestFunctions(base.EasyFormTestCase):

    ''' test save data adapter '''

    def afterSetUp(self):
        base.EasyFormTestCase.afterSetUp(self)
        self.folder.invokeFactory('EasyForm', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def createSaver(self):
        ''' Creates FormCustomScript object '''
        # 1. Create custom script adapter in the form folder
        self.portal.REQUEST['form.widgets.title'] = u'Saver'
        self.portal.REQUEST['form.widgets.__name__'] = u'saver'
        self.portal.REQUEST['form.widgets.description'] = u''
        self.portal.REQUEST['form.widgets.factory'] = ['Save Data']
        self.portal.REQUEST['form.buttons.add'] = u'Add'
        view = self.ff1.restrictedTraverse('actions/@@add-action')
        view.update()
        form = view.form_instance
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        # 2. Check that creation succeeded
        actions = get_actions(self.ff1)
        self.assertTrue('saver' in actions)

    def testSavedDataView(self):
        ''' test saved data view '''

        self.createSaver()

        view = self.ff1.restrictedTraverse('saveddata')
        self.assertEqual(view.items(), [('saver', u'Saver')])

    def testSaverDataFormExtraData(self):
        ''' test saver data form extra data'''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic='test subject', replyto='test@test.org', comments='test comments')
        saver.ExtraData = ('dt',)
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse('@@actions')
        view = view.publishTraverse(view.request, 'saver')
        view = view.publishTraverse(view.request, 'data')
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {'items': 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]['id'], item[0])
        self.assertEqual(item[1]['topic'], 'test subject')
        self.assertEqual(item[1]['replyto'], 'test@test.org')
        self.assertEqual(item[1]['comments'], 'test comments')
        self.assertTrue(' ' in item[1]['dt'])

    def testSaverDataFormShowFields(self):
        ''' test saver data form show fields '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic='test subject', replyto='test@test.org', comments='test comments')
        saver.showFields = ('topic', 'comments')
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse('@@actions')
        view = view.publishTraverse(view.request, 'saver')
        view = view.publishTraverse(view.request, 'data')
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {'items': 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]['id'], item[0])
        self.assertEqual(item[1]['topic'], 'test subject')
        self.assertEqual(item[1]['comments'], 'test comments')
        self.assertTrue('replyto' not in item[1])

    def testSaverDataFormOneItem(self):
        ''' test saver data form one item '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse('@@actions')
        view = view.publishTraverse(view.request, 'saver')
        view = view.publishTraverse(view.request, 'data')
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {'items': 1})
        item = form.get_items()[0]
        self.assertEqual(item[1]['id'], item[0])
        self.assertEqual(item[1]['topic'], 'test subject')
        self.assertEqual(item[1]['replyto'], 'test@test.org')
        self.assertEqual(item[1]['comments'], 'test comments')

    def testSaverDataForm(self):
        ''' test saver data form '''

        self.createSaver()

        view = self.ff1.restrictedTraverse('@@actions')
        view = view.publishTraverse(view.request, 'saver')
        view = view.publishTraverse(view.request, 'data')
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {'items': 0})
        self.assertEqual([i for i in form.get_items()], [])

    def testSaver(self):
        ''' test save data adapter action '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        self.assertEqual(saver.itemsSaved(), 0)

        res = saver.getSavedFormInputForEdit()
        self.assertEqual(res, '')

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)

        res = saver.getSavedFormInputForEdit()
        self.assertEqual(
            res.strip(), 'test@test.org,test subject,test comments')

    def testSaverExtraData(self):
        ''' test save data adapter action '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.ExtraData = ('dt',)
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        self.assertTrue('dt' in saver.getSavedFormInput()[0])

    def testSaverDownload(self):
        ''' test save data '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.download(request.response)
        res = request.response.stdout.getvalue()
        self.assertTrue('Content-Type: text/comma-separated-values' in res)
        self.assertTrue(
            'Content-Disposition: attachment; filename="saver.csv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit() in res)

    def testSaverDownloadTSV(self):
        ''' test save data '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.DownloadFormat = 'tsv'
        saver.download(request.response)
        res = request.response.stdout.getvalue()
        self.assertTrue('Content-Type: text/tab-separated-values' in res)
        self.assertTrue(
            'Content-Disposition: attachment; filename="saver.tsv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit(delimiter='\t') in res)

    def testSaverDownloadWithTitles(self):
        ''' test save data '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.UseColumnNames = True
        saver.download(request.response)
        res = request.response.stdout.getvalue()
        self.assertTrue('Content-Type: text/comma-separated-values' in res)
        self.assertTrue(
            'Content-Disposition: attachment; filename="saver.csv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit(header=True) in res)

    def testSaverDownloadExtraData(self):
        ''' test save data '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.ExtraData = ('dt', 'HTTP_USER_AGENT')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        saver.download(request.response)
        res = request.response.stdout.getvalue()
        self.assertTrue('Content-Type: text/comma-separated-values' in res)
        self.assertTrue(
            'Content-Disposition: attachment; filename="saver.csv"' in res)
        self.assertTrue(saver.getSavedFormInputForEdit() in res)

    def testSaverSavedFormInput(self):
        ''' test save data adapter action and direct access to SavedFormInput '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        row = iter(saver.getSavedFormInput()).next()
        self.assertEqual(len(row), 4)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)
        self.assertEqual(saver.itemsSaved(), 2)

        saver.clearSavedFormInput()
        self.assertEqual(saver.itemsSaved(), 0)

    def testSetSavedFormInput(self):
        ''' test setSavedFormInput functionality '''

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.getSavedFormInputForEdit(), '')

        # save a row
        fields = list(get_fields(self.ff1))
        saver.addDataRow(dict(zip(fields, ['one', 'two', 'three'])))
        self.assertEqual(saver.itemsSaved(), 1)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1], dict(zip(['id'] + fields, [items[0][0], 'one', 'two', 'three'])))
        self.assertEqual(saver.getSavedFormInputForEdit(), 'one,two,three\r\n')

        # save a couple of \n-delimited rows - \n eol
        saver.addDataRow(dict(zip(fields, ['four', 'five', 'six'])))
        self.assertEqual(saver.itemsSaved(), 2)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1], dict(zip(['id'] + fields, [items[0][0], 'one', 'two', 'three'])))
        self.assertEqual(
            items[1][1], dict(zip(['id'] + fields, [items[1][0], 'four', 'five', 'six'])))
        self.assertEqual(
            saver.getSavedFormInputForEdit(), 'one,two,three\r\nfour,five,six\r\n')

        # save empty string
        saver.clearSavedFormInput()
        self.assertEqual(saver.itemsSaved(), 0)
        self.assertEqual(saver.getSavedFormInputForEdit(), '')

    def testEditSavedFormInput(self):
        ''' test manage_saveData functionality '''

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # save a row
        fields = list(get_fields(self.ff1))
        # saver.savedFormInput = 'one,two,three'
        saver.addDataRow(dict(zip(fields, ['one', 'two', 'three'])))
        self.assertEqual(saver.itemsSaved(), 1)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1], dict(zip(['id'] + fields, [items[0][0], 'one', 'two', 'three'])))

    def testDeleteSavedFormInput(self):
        ''' test manage_deleteData functionality '''

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # save a few rows
        fields = list(get_fields(self.ff1))
        saver.addDataRow(dict(zip(fields, ['one', 'two', 'three'])))
        saver.addDataRow(dict(zip(fields, ['four', 'five', 'six'])))
        saver.addDataRow(dict(zip(fields, ['seven', 'eight', 'nine'])))
        self.assertEqual(saver.itemsSaved(), 3)

        # saver.manage_deleteData(saver._storage.keys()[1])
        saver.delDataRow(saver.getSavedFormInputItems()[1][0])
        self.assertEqual(saver.itemsSaved(), 2)
        items = saver.getSavedFormInputItems()
        self.assertEqual(
            items[0][1], dict(zip(['id'] + fields, [items[0][0], 'one', 'two', 'three'])))
        self.assertEqual(
            items[1][1], dict(zip(['id'] + fields, [items[1][0], 'seven', 'eight', 'nine'])))

    def testSaverInputAsDictionaries(self):
        ''' test save data adapter's InputAsDictionaries '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # self.ff1.setActionAdapter(('saver',))

        # self.assertEqual(saver.inputAsDictionaries, saver.InputAsDictionaries)

        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)
        # errors = self.ff1.fgvalidate(REQUEST=request)
        # self.assertEqual(errors, {})

        self.assertEqual(saver.itemsSaved(), 1)

        iad = saver.getSavedFormInput()
        row = iter(iad).next()
        self.assertEqual(len(row), 4)
        self.assertEqual(row['topic'], 'test subject')

    def testSaverColumnNames(self):
        ''' test save data adapter's getColumnNames function '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        cn = saver.getColumnNames()
        self.assertTrue(len(cn) == 3)
        self.assertTrue(cn[0] == 'replyto')
        self.assertTrue(cn[1] == 'topic')
        self.assertTrue(cn[2] == 'comments')

        # Use selective field saving
        saver.showFields = ('topic', 'comments')
        cn = saver.getColumnNames()
        self.assertTrue(len(cn) == 2)
        self.assertTrue(cn[0] == 'topic')
        self.assertTrue(cn[1] == 'comments')
        saver.showFields = tuple()

        # Add an extra column
        saver.ExtraData = ('dt',)
        cn = saver.getColumnNames()
        self.assertTrue(len(cn) == 4)
        self.assertTrue(cn[3] == 'dt')

        # add a label field -- should not show up in column names
        # self.ff1.invokeFactory('FormLabelField', 'alabel')
        # cn = saver.getColumnNames()
        # self.assertTrue(len(cn) == 4)

        # add a form field -- should show up in column names before 'dt'
        # self.ff1.invokeFactory('FormFileField', 'afile')
        # cn = saver.getColumnNames()
        # self.assertTrue(len(cn) == 5)
        # self.assertTrue(cn[3] == 'afile')
        # self.assertTrue(cn[4] == 'dt')

    def testSaverColumnTitles(self):
        ''' test save data adapter's getColumnTitles function '''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        cn = saver.getColumnTitles()
        self.assertTrue(len(cn) == 3)
        self.assertTrue(cn[0] == 'Your E-Mail Address')
        self.assertTrue(cn[1] == 'Subject')
        self.assertTrue(cn[2] == 'Comments')

        # Add an extra column
        saver.ExtraData = ('dt',)
        cn = saver.getColumnTitles()
        self.assertTrue(len(cn) == 4)
        self.assertTrue(cn[3] == 'Posting Date/Time')

    def testSaverSelectiveFieldSaving(self):
        ''' Test selective inclusion of fields in the data'''

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        saver.showFields = ('topic', 'comments')

        request = FakeRequest(add_auth=True, method='POST',
                              topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        self.assertEqual(saver.itemsSaved(), 1)
        row = iter(saver.getSavedFormInput()).next()
        self.assertEqual(len(row), 3)
        self.assertEqual(row['topic'], 'test subject')
        self.assertEqual(row['comments'], 'test comments')

    # the csrf test has moved to browser.txt


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFunctions))
    return suite
