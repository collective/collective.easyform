# Integration tests specific to save-data adapter.
#

import sys
import plone.protect
from Products.CMFCore.utils import getToolByName
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from collective.formulator.api import get_actions, get_fields
from collective.formulator.tests import base

# dummy class


class cd:
    pass


def FakeRequest(method="GET", add_auth=False, **kwargs):
    environ = {}
    environ.setdefault('SERVER_NAME', 'foo')
    environ.setdefault('SERVER_PORT', '80')
    environ.setdefault('REQUEST_METHOD', method)
    request = HTTPRequest(sys.stdin,
                          environ,
                          HTTPResponse(stdout=sys.stdout))
    request.form = kwargs
    if add_auth:
        request.form['_authenticator'] = plone.protect.createToken()
    return request


class TestFunctions(base.FormulatorTestCase):

    """ test save data adapter """

    def afterSetUp(self):
        base.FormulatorTestCase.afterSetUp(self)
        self.folder.invokeFactory('Formulator', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def createSaver(self):
        """ Creates FormCustomScript object """
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
        self.assertTrue('saver' in actions)

    def testSavedDataView(self):
        """ test saved data view """

        self.createSaver()

        view = self.ff1.restrictedTraverse("saveddata")
        self.assertEqual(view.items(), [('saver', u'Saver')])

    def testSaverDataFormOneItem(self):
        """ test saver data form one item """

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        self.assertEqual(saver.itemsSaved(), 0)
        request = FakeRequest(
            topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)

        view = self.ff1.restrictedTraverse("@@actions")
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
        """ test saver data form """

        self.createSaver()

        view = self.ff1.restrictedTraverse("@@actions")
        view = view.publishTraverse(view.request, 'saver')
        view = view.publishTraverse(view.request, 'data')
        view.update()
        form = view.form_instance
        message = form.description()
        self.assertEqual(message.mapping, {'items': 0})
        self.assertEqual([i for i in form.get_items()], [])

    def testSaver(self):
        """ test save data adapter action """

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # self.ff1.setActionAdapter(('saver',))
        #self.assertEqual(self.ff1.actionAdapter, ('saver',))

        # print "|%s|" % saver.SavedFormInput
        self.assertEqual(saver.itemsSaved(), 0)

        #res = saver.getSavedFormInputForEdit()
        #self.assertEqual(res, '')

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        #view = self.ff1.restrictedTraverse('view')
        #form = view.form_instance
        # form.processActions(request.form)
        saver.onSuccess(request.form, request)
        #errors = self.ff1.fgvalidate(REQUEST=request)
        #self.assertEqual(errors, {})

        self.assertEqual(saver.itemsSaved(), 1)

        #res = saver.getSavedFormInputForEdit()
        # self.assertEqual(
            # res.strip(), 'test@test.org,test subject,test comments')

    def testSaverSavedFormInput(self):
        """ test save data adapter action and direct access to SavedFormInput """

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # self.ff1.setActionAdapter(('saver',))

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)
        #errors = self.ff1.fgvalidate(REQUEST=request)
        #self.assertEqual(errors, {})

        self.assertEqual(saver.itemsSaved(), 1)
        row = iter(saver.getSavedFormInput()).next()
        self.assertEqual(len(row), 4)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)
        #errors = self.ff1.fgvalidate(REQUEST=request)
        #self.assertEqual(errors, {})
        self.assertEqual(saver.itemsSaved(), 2)

        saver._storage.clear()
        self.assertEqual(saver.itemsSaved(), 0)

    def testSetSavedFormInput(self):
        """ test setSavedFormInput functionality """

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # save a row
        fields = list(get_fields(self.ff1))
        #saver.savedFormInput = 'one,two,three'
        saver.addDataRow(dict(zip(fields, ['one', 'two', 'three'])))
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], dict(zip(['id'] + fields, [saver._storage.keys()[0], 'one', 'two', 'three'])))

        # save a couple of \n-delimited rows - \n eol
        #saver.savedFormInput = 'one,two,three\nfour,five,six'
        saver.addDataRow(dict(zip(fields, ['four', 'five', 'six'])))
        self.assertEqual(saver.itemsSaved(), 2)
        self.assertEqual(
            saver._storage.values()[0], dict(zip(['id'] + fields, [saver._storage.keys()[0], 'one', 'two', 'three'])))
        self.assertEqual(
            saver._storage.values()[1], dict(zip(['id'] + fields, [saver._storage.keys()[1], 'four', 'five', 'six'])))

        # save a couple of \n-delimited rows -- \r\n eol
        #saver.savedFormInput = 'one,two,three\r\nfour,five,six'
        #self.assertEqual(saver.itemsSaved(), 2)

        # save a couple of \n-delimited rows -- \n\n double eol
        #saver.savedFormInput = 'one,two,three\n\nfour,five,six'
        #self.assertEqual(saver.itemsSaved(), 2)

        # save empty string
        saver._storage.clear()
        self.assertEqual(saver.itemsSaved(), 0)

        # save empty list
        #saver.savedFormInput = tuple()
        #self.assertEqual(saver.itemsSaved(), 0)

    def ttestSetSavedFormInputAlternateDelimiter(self):
        """ test setSavedFormInput functionality when an alternate csv delimiter
            has been specified
        """
        # set prefered delimiter
        pft = getToolByName(self.portal, 'formgen_tool')
        alt_delimiter = '|'
        pft.setDefault('csv_delimiter', alt_delimiter)
        # set up saver
        self.createSaver()
        saver = get_actions(self.ff1)['saver']

        # build and save a row
        row1 = alt_delimiter.join(('one', 'two', 'three'))
        saver.savedFormInput = row1
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._storage[0], ['one', 'two', 'three'])

        # save a couple of \n-delimited rows - \n eol
        row2 = alt_delimiter.join(('four', 'five', 'six'))
        saver.savedFormInput = '%s\n%s' % (row1, row2)
        self.assertEqual(saver.itemsSaved(), 2)
        self.assertEqual(saver._storage[0], ['one', 'two', 'three'])
        self.assertEqual(saver._storage[1], ['four', 'five', 'six'])

        # save a couple of \n-delimited rows -- \r\n eol
        saver.savedFormInput = '%s\r\n%s' % (row1, row2)
        self.assertEqual(saver.itemsSaved(), 2)

        # save a couple of \n-delimited rows -- \n\n double eol
        saver.savedFormInput = '%s\n\n%s' % (row1, row2)
        self.assertEqual(saver.itemsSaved(), 2)

        # save empty string
        saver.savedFormInput = ''
        self.assertEqual(saver.itemsSaved(), 0)

        # save empty list
        saver.savedFormInput = tuple()
        self.assertEqual(saver.itemsSaved(), 0)

    def testEditSavedFormInput(self):
        """ test manage_saveData functionality """

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # save a row
        fields = list(get_fields(self.ff1))
        #saver.savedFormInput = 'one,two,three'
        saver.addDataRow(dict(zip(fields, ['one', 'two', 'three'])))
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], dict(zip(['id'] + fields, [saver._storage.keys()[0], 'one', 'two', 'three'])))
        """
        data = cd()
        setattr(data, 'item-0', 'four')
        setattr(data, 'item-1', 'five')
        setattr(data, 'item-2', 'six')

        # We should need an authenticator
        self.assertRaises(
            zExceptions.Forbidden, saver.manage_saveData, *[saver._storage.keys()[0], data])

        saver.REQUEST = FakeRequest(add_auth=True, method="POST")
        saver.manage_saveData(saver._storage.keys()[0], data)

        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], ['four', 'five', 'six'])
        """

    def ttestEditSavedFormInputWithAlternateDelimiter(self):
        """ test manage_saveData functionality when an alternate csv delimiter is used """

        # set prefered delimiter
        pft = getToolByName(self.portal, 'formgen_tool')
        alt_delimiter = '|'
        pft.setDefault('csv_delimiter', alt_delimiter)

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # save a row
        saver.savedFormInput = 'one|two|three'
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], ['one', 'two', 'three'])

        data = cd()
        setattr(data, 'item-0', 'four')
        setattr(data, 'item-1', 'five')
        setattr(data, 'item-2', 'six')

        saver.REQUEST = FakeRequest(add_auth=True, method="POST")
        saver.manage_saveData(saver._storage.keys()[0], data)
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], ['four', 'five', 'six'])

    def ttestRetrieveDataSavedBeforeSwitchingDelimiter(self):
        """ test manage_saveData functionality when an alternate csv delimiter is used """

        # set up saver
        self.createSaver()
        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # save a row
        saver.savedFormInput = 'one,two,three'
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], ['one', 'two', 'three'])

        # switch prefered delimiter
        #pft = getToolByName(self.portal, 'formgen_tool')
        #alt_delimiter = '|'
        #pft.setDefault('csv_delimiter', alt_delimiter)

        # verify we can retrieve based on new delimiter
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(
            saver._storage.values()[0], ['one', 'two', 'three'])

    def testDeleteSavedFormInput(self):
        """ test manage_deleteData functionality """

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
        del saver._storage[saver._storage.keys()[1]]
        self.assertEqual(saver.itemsSaved(), 2)
        self.assertEqual(
            saver._storage.values()[0], dict(zip(['id'] + fields, [saver._storage.keys()[0], 'one', 'two', 'three'])))
        self.assertEqual(
            saver._storage.values()[1], dict(zip(['id'] + fields, [saver._storage.keys()[1], 'seven', 'eight', 'nine'])))

    def testSaverInputAsDictionaries(self):
        """ test save data adapter's InputAsDictionaries """

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # self.ff1.setActionAdapter(('saver',))

        #self.assertEqual(saver.inputAsDictionaries, saver.InputAsDictionaries)

        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(
            add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)
        #errors = self.ff1.fgvalidate(REQUEST=request)
        #self.assertEqual(errors, {})

        self.assertEqual(saver.itemsSaved(), 1)

        iad = saver.getSavedFormInput()
        row = iter(iad).next()
        self.assertEqual(len(row), 4)
        self.assertEqual(row['topic'], 'test subject')

    def testSaverColumnNames(self):
        """ test save data adapter's getColumnNames function """

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # self.ff1.setActionAdapter(('saver',))

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
        #self.ff1.invokeFactory('FormLabelField', 'alabel')
        #cn = saver.getColumnNames()
        #self.assertTrue(len(cn) == 4)

        # add a form field -- should show up in column names before 'dt'
        #self.ff1.invokeFactory('FormFileField', 'afile')
        #cn = saver.getColumnNames()
        #self.assertTrue(len(cn) == 5)
        #self.assertTrue(cn[3] == 'afile')
        #self.assertTrue(cn[4] == 'dt')

    def testSaverColumnTitles(self):
        """ test save data adapter's getColumnTitles function """

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']

        # self.ff1.setActionAdapter(('saver',))

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
        """ Test selective inclusion of fields in the data"""

        self.createSaver()

        self.assertTrue('saver' in get_actions(self.ff1))
        saver = get_actions(self.ff1)['saver']
        saver.showFields = ('topic', 'comments')

        # self.ff1.setActionAdapter(('saver',))

        request = FakeRequest(add_auth=True, method='POST',
                              topic='test subject', replyto='test@test.org', comments='test comments')
        saver.onSuccess(request.form, request)
        #errors = self.ff1.fgvalidate(REQUEST=request)
        #self.assertEqual(errors, {})

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
