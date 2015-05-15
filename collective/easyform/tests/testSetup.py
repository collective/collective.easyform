# -*- coding: utf-8 -*-
#
# Test EasyForm initialisation and set-up
#

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from collective.easyform.tests import base
import Products


def getAddPermission(product, name):
    ''' find the add permission for a meta_type '''

    name = '{0}: {1}'.format(product, name)
    for mt in Products.meta_types:
        if mt['name'] == name:
            return mt['permission']
    return ''


class TestInstallation(base.EasyFormTestCase):

    '''Ensure product is properly installed'''

    def afterSetUp(self):
        base.EasyFormTestCase.afterSetUp(self)

        self.types = self.portal.portal_types
        self.properties = self.portal.portal_properties
        self.at_tool = self.portal.archetype_tool
        self.controlpanel = self.portal.portal_controlpanel

        self.metaTypes = ('EasyForm',)

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.assertTrue(t in self.types.objectIds())

    def testTypeActions(self):
        # hide properties/references tabs
        for typ in self.metaTypes:
            for act in self.types[typ].listActions():
                if act.id in ['metadata', 'references']:
                    self.assertFalse(act.visible)
                if act.id in ['actions', 'fields']:
                    self.assertTrue(act.visible)

    def testArchetypesToolCatalogRegistration(self):
        for t in self.metaTypes:
            self.assertEqual(1, len(self.at_tool.getCatalogsByType(t)))
            self.assertEqual(
                'portal_catalog', self.at_tool.getCatalogsByType(t)[0].getId())

    def ttestControlPanelConfigletInstalled(self):
        self.assertTrue(
            'EasyForm' in [action.id for action in self.controlpanel.listActions()])

    def ttestAddPermissions(self):
        ''' Test to make sure add permissions are as intended '''

        ADD_CONTENT_PERMISSION = 'EasyForm: Add Content'
        CSA_ADD_CONTENT_PERMISSION = 'EasyForm: Add Custom Scripts'
        MA_ADD_CONTENT_PERMISSION = 'EasyForm: Add Mailers'
        SDA_ADD_CONTENT_PERMISSION = 'EasyForm: Add Data Savers'

        self.assertEqual(
            getAddPermission('EasyForm', 'EasyForm'), ADD_CONTENT_PERMISSION)
        self.assertEqual(
            getAddPermission('EasyForm', 'Mailer Adapter'), MA_ADD_CONTENT_PERMISSION)
        self.assertEqual(
            getAddPermission('EasyForm', 'Save Data Adapter'), SDA_ADD_CONTENT_PERMISSION)
        self.assertEqual(
            getAddPermission('EasyForm', 'Custom Script Adapter'), CSA_ADD_CONTENT_PERMISSION)

    def testActionsInstalled(self):
        # self.setRoles(['Manager', ])
        self.assertTrue(
            self.portal.portal_actions.getActionInfo('object_buttons/export'))
        self.assertTrue(
            self.portal.portal_actions.getActionInfo('object_buttons/import'))
        self.assertTrue(
            self.portal.portal_actions.getActionInfo('object_buttons/saveddata'))

    def ttest_FormGenTool(self):
        self.assertTrue(getToolByName(self.portal, 'formgen_tool'))

    def testModificationsToPropSheetLinesNotPuged(self):
        property_mappings = [{
            'propsheet': 'site_properties',
            'added_props': [
                'use_folder_tabs',
                'typesLinkToFolderContentsInFC',
                'default_page_types',
            ]
        }]

        # add garbage prop element to each lines property
        for mapping in property_mappings:
            sheet = self.properties[mapping['propsheet']]
            for lines_prop in mapping['added_props']:
                propitems = list(sheet.getProperty(lines_prop))
                propitems.append('foo')
                sheet.manage_changeProperties({lines_prop: propitems})

        # reinstall
        qi = self.portal.portal_quickinstaller
        qi.reinstallProducts(['collective.easyform'])

        # now make sure our garbage values survived the reinstall
        for mapping in property_mappings:
            sheet = self.properties[mapping['propsheet']]
            for lines_prop in mapping['added_props']:
                self.assertTrue('foo' in sheet.getProperty(lines_prop),
                                "Our garbage item didn't survive reinstall for property {0}"
                                " within property sheet {1}".format(lines_prop, mapping['propsheet']))

    def test_EasyFormInDefaultPageTypes(self):
        propsTool = getToolByName(self.portal, 'portal_properties')
        siteProperties = getattr(propsTool, 'site_properties')
        defaultPageTypes = list(
            siteProperties.getProperty('default_page_types'))
        self.assertTrue('EasyForm' in defaultPageTypes)

    def testTypeViews(self):
            self.assertEqual(
                self.types.EasyForm.getAvailableViewMethods(self.types), ('view',))


class TestContentCreation(base.EasyFormTestCase):

    '''Ensure content types can be created and edited'''

    fieldTypes = [
        'FormSelectionField',
        'FormMultiSelectionField',
        'FormLabelField',
        'FormDateField',
        'FormLinesField',
        'FormIntegerField',
        'FormBooleanField',
        'FormPasswordField',
        'FormFixedPointField',
        'FormStringField',
        'FormTextField',
        'FormRichTextField',
        'FormFileField',
    ]
    # if base.haveRecaptcha:
    #    fieldTypes.append('FormCaptchaField')
    fieldTypes = tuple(fieldTypes)

    adapterTypes = (
        'FormSaveDataAdapter',
        'FormMailerAdapter',
    )

    thanksTypes = (
        'FormThanksPage',
    )

    fieldsetTypes = (
        'FieldsetFolder',
    )

    sampleContentIds = ('mailer', 'replyto', 'topic', 'comments', 'thank-you')

    def afterSetUp(self):
        base.EasyFormTestCase.afterSetUp(self)
        self.folder.invokeFactory('EasyForm', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testCreateEasyForm(self):
        self.assertTrue('ff1' in self.folder.objectIds())

    def testSampleContent(self):
        # check embedded content
        oi = self.ff1.objectIds()
        for id in self.sampleContentIds:
            self.assertTrue(id in oi)

    def testSampleMailerSetup(self):
        self.assertEqual(self.ff1.actionAdapter, ('mailer',))
        self.assertEqual(self.ff1.mailer.replyto_field, 'replyto')
        self.assertEqual(self.ff1.mailer.subject_field, 'topic')
        self.assertEqual(self.ff1.mailer.thanksPage, 'thank-you')

    def testEasyFormCanSetDefaultPage(self):
        self.assertEqual(self.ff1.canSetDefaultPage(), False)

    def testEditEasyForm(self):
        self.ff1.setTitle('A title')
        self.ff1.setDescription('A description')

        self.assertEqual(self.ff1.Title(), 'A title')
        self.assertEqual(self.ff1.Description(), 'A description')

    def testCreateFields(self):
        for f in self.fieldTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            self.assertTrue(fname in self.ff1.objectIds())

    def testCreateAdapters(self):
        for f in self.adapterTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            self.assertTrue(fname in self.ff1.objectIds())
            self.assertTrue(hasattr(self.ff1[fname], 'onSuccess'))

    def testCreateThanksPages(self):
        for f in self.thanksTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            self.assertTrue(fname in self.ff1.objectIds())
            self.assertTrue(hasattr(self.ff1[fname], 'displayFields'))

    def testCreateFieldset(self):
        for f in self.fieldsetTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            self.assertTrue(fname in self.ff1.objectIds())

    def testCreateFieldsinFieldset(self):
        fname = 'FieldsetFolder1'
        self.ff1.invokeFactory('FieldsetFolder', fname)
        self.assertTrue(fname in self.ff1.objectIds())
        fs = self.ff1[fname]
        for f in self.fieldTypes:
            fname = '{0}1fs'.format(f)
            fs.invokeFactory(f, fname)
            self.assertTrue(fname in fs.objectIds())

        # Things that shouldn't fit in a fieldset folder
        self.assertRaises(ValueError, fs.invokeFactory, 'EasyForm', 'ffinf')
        self.assertRaises(
            ValueError, fs.invokeFactory, 'FormThanksPage', 'ffinf')
        self.assertRaises(
            ValueError, fs.invokeFactory, 'FieldsetFolder', 'ffinf')
        self.assertRaises(
            ValueError, fs.invokeFactory, 'FormMailerAdapter', 'ffinf')

        # try finding the fields
        for f in self.fieldTypes:
            fname = '{0}1fs'.format(f)
            self.assertTrue(self.ff1.findFieldObjectByName(fname))

    def testFgFieldsDisplayOnly(self):
        ''' Make sure fgFields displayOnly parameter correctly excludes
            labels and fieldset markers
        '''

        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.assertTrueEqual(wExtras, noExtras)

        self.ff1.invokeFactory('FieldsetFolder', 'FieldsetFolder1')
        self.ff1['FieldsetFolder1'].invokeFactory('FormStringField', 'fsf')

        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.assertTrueEqual(wExtras, noExtras + 2)

        self.ff1.invokeFactory('FormLabelField', 'flf')
        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.assertTrueEqual(wExtras, noExtras + 3)

        self.ff1.invokeFactory('FormRichLabelField', 'frlf')
        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.assertTrueEqual(wExtras, noExtras + 4)

    def testEditField(self):
        for f in self.fieldTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            f1.setTitle('Field title')
            f1.setDescription('Field description')

            self.assertEqual(f1.Title(), 'Field title')
            self.assertEqual(f1.fgField.widget.label, 'Field title')
            self.assertEqual(f1.Description(), 'Field description')
            self.assertEqual(
                f1.fgField.widget.description, 'Field description')

    def testTALESFieldValidation(self):
        for f in self.fieldTypes:
            if f != 'FormLabelField':
                fname = '{0}1'.format(f)
                self.ff1.invokeFactory(f, fname)
                f1 = getattr(self.ff1, fname)
                self.assertEqual(f1.getFgTValidator(), False)
                f1.setFgTValidator('python:True')
                self.assertEqual(f1.getFgTValidator(), True)

    def testEditAdapter(self):
        for f in self.adapterTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            f1.setTitle('title')
            f1.setDescription('description')

            self.assertEqual(f1.Title(), 'title')
            self.assertEqual(f1.Description(), 'description')

    def testMailerZPTBody(self):
        fname = 'FormMailerAdapter1'
        self.ff1.invokeFactory('FormMailerAdapter', fname)
        f1 = getattr(self.ff1, fname)
        self.assertTrue(f1.getBody_pt(fields=[], wrappedFields=[]))

    def testEditThanksPages(self):
        for f in self.thanksTypes:
            fname = '{0}1'.format(f)
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            f1.setTitle('title')
            f1.setDescription('description')

            self.assertEqual(f1.Title(), 'title')
            self.assertEqual(f1.Description(), 'description')

    def testCreateFieldsAdaptersOutsideEasyForm(self):
        for f in self.fieldTypes + self.adapterTypes + self.thanksTypes + self.fieldsetTypes:
            try:
                self.folder.invokeFactory(f, 'f1')
            except (Unauthorized, ValueError):
                return
            self.fail(
                'Expected error when creating form field or adapter outside form folder.')

    def testBadIdField(self):
        # test for tracker # 32 - Field with id 'language' causes problems with
        # PTS

        from Products.CMFCore.exceptions import BadRequest

        fname = 'test_field'
        self.ff1.invokeFactory('FormStringField', fname)
        f1 = getattr(self.ff1, fname)

        self.assertRaises(BadRequest, f1.setId, 'language')

        # also not such a good idea ...
        self.assertRaises(BadRequest, f1.setId, 'form')

    def testFieldRename(self):
        '''
        renaming a field should change the __name__ attribute
        of the embedded fgField; tracker issue # 42
        '''

        self.ff1.invokeFactory('FormStringField', 'spam_and_eggs')
        self.assertTrue('spam_and_eggs' in self.ff1.objectIds())

        myField = getattr(self.ff1, 'spam_and_eggs')
        fgf = getattr(myField, 'fgField')
        self.assertEqual(fgf.__name__, 'spam_and_eggs')

        # XXX TODO: figure out what's wrong with this:
        # self.ff1.manage_renameObject('spam_and_eggs', 'spam_spam_and_eggs')
        # self.assertEqual(fgf.__name__, 'spam_spam_and_eggs')

    def testFieldsetRename(self):
        '''
        renaming a fieldset should change the __name__ attribute
        of the embedded fsStartField
        '''

        self.ff1.invokeFactory('FieldsetFolder', 'fsfolder1')
        self.assertTrue('fsfolder1' in self.ff1.objectIds())

        myField = getattr(self.ff1, 'fsfolder1')
        fgf = getattr(myField, 'fsStartField')
        self.assertEqual(fgf.__name__, 'fsfolder1')

    def testFieldsetPlusDisplayList(self):
        ''' Test for issue  # 44 -- Presence of fieldset causes an attribute error
        '''

        # create fieldset
        self.ff1.invokeFactory('FieldsetFolder', 'fsf1')
        self.assertTrue(self.ff1.fgFieldsDisplayList())

    def testUtfInFieldTitle(self):
        ''' test for issue # 102, 104: utf8, non-ascii in field title or description
        '''

        self.ff1.invokeFactory('FormStringField', 'sf1',
                               title='Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf8'))

        self.ff1.sf1.setDescription(
            'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf8'))
        # force a reindex
        self.ff1.sf1.reindexObject()

    def testUtfInFormTitle(self):
        ''' test for utf8, non-ascii in form title or description
        '''

        self.folder.invokeFactory('EasyForm', 'ff2',
                                  title='Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf8'))

        self.folder.ff2.setDescription(
            'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf8'))
        # force a reindex
        self.folder.ff2.reindexObject()

    def testBadIds(self):
        ''' test ids that cause problems.
            We shouldn't be able to create objects with ids known
            to be troublesome.
            Also, all fields in all fieldsets must have unique ids.
        '''

        # should be OK:
        self.assertTrue(self.ff1.checkIdAvailable('somethingunique8723'))

        # bad ids should fail
        self.assertFalse(self.ff1.checkIdAvailable('zip'))
        self.assertFalse(self.ff1.checkIdAvailable('location'))
        self.assertFalse(self.ff1.checkIdAvailable('language'))

        # existing ids should fail
        self.ff1.invokeFactory('FormStringField', 'sf1')
        self.assertFalse(self.ff1.checkIdAvailable('sf1'))

        # test in fieldset folder
        self.ff1.invokeFactory('FieldsetFolder', 'fsf1')
        fsf1 = self.ff1.fsf1
        self.assertTrue(fsf1.checkIdAvailable('somethingunique8723'))
        self.assertFalse(fsf1.checkIdAvailable('zip'))

        # We should also not be able to create a fieldset folder field
        # with an id the same as one in the parent form folder
        self.assertFalse(fsf1.checkIdAvailable('sf1'))
        # nor in the fieldset folder itself
        fsf1.invokeFactory('FormStringField', 'sf2')
        self.assertFalse(fsf1.checkIdAvailable('sf2'))

        # Let's try it in a sibling fieldset folder
        self.ff1.invokeFactory('FieldsetFolder', 'fsf2')
        fsf2 = self.ff1.fsf2
        self.assertTrue(fsf2.checkIdAvailable('somethingunique8723'))
        self.assertFalse(fsf2.checkIdAvailable('sf1'))
        self.assertFalse(fsf2.checkIdAvailable('sf2'))


class TestGPG(base.EasyFormTestCase):

    ''' test ya_gpg.py '''

    def test_gpg(self):
        from collective.easyform.content.ya_gpg import gpg, GPGError

        if gpg is None:
            print '\nSkipping GPG tests; gpg binary not found'
        else:
            self.assertRaises(GPGError, gpg.encrypt, 'spam', 'eggs')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    # suite.addTest(makeSuite(TestContentCreation))
    # suite.addTest(makeSuite(TestGPG))
    return suite
