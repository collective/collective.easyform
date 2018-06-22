# -*- coding: utf-8 -*-
#
# Integeration tests specific to the mailer
#

from collective.easyform.browser.view import EasyFormForm
from collective.easyform.tests import base
from os.path import dirname
from os.path import join
from plone import api
from plone.namedfile.file import NamedFile


class TestFunctions(base.EasyFormTestCase):
    """ Test mailer action """

    def afterSetUp(self):
        super(TestFunctions, self).afterSetUp()
        ff1_id = self.folder.invokeFactory('EasyForm', 'ff1')
        self.ff1 = self.folder[ff1_id]

    def LoadRequestForm(self, **kwargs):
        request = self.layer['request']
        request.form.clear()
        prefix = 'form.widgets.'
        for key in kwargs.keys():
            request.form[prefix + key] = kwargs[key]
        return request

    def test_thankspage(self):
        """ Test thankspage """

        data = {
            'topic': 'test subject',
            'comments': 'test comments',
            'replyto': 'foo@bar.com'
        }
        request = self.LoadRequestForm(**data)
        request.method = 'POST'
        form = EasyFormForm(self.ff1, request)()
        self.assertIn('Thanks for your input.', form)
        self.assertIn(
            '<span id="form-widgets-replyto" class="text-widget required textline-field">foo@bar.com</span>',  # noqa
            form)

    def test_thankspage_filter(self):
        """ Test thankspage """
        self.ff1.showAll = False
        self.ff1.showFields = ['comments']
        data = {
            'topic': 'test subject',
            'comments': 'test comments',
            'replyto': 'foo@bar.com'
        }
        request = self.LoadRequestForm(**data)
        request.method = 'POST'
        form = EasyFormForm(self.ff1, request)()
        self.assertIn('Thanks for your input.', form)
        self.assertNotIn('subject', form)
        self.assertIn('test comments', form)

    def test_thankspage_radio(self):
        self.ff1.showAll = True
        field_template = api.content.create(
            self.layer['portal'], 'File', id='easyform_default_fields.xml')
        with open(join(dirname(__file__), 'fixtures', 'radio_form.xml')) as f:
            filecontent = NamedFile(f.read(), contentType='application/xml')
        field_template.file = filecontent

        data = {'yes': 'true', 'yes-empty-marker': 1}
        request = self.LoadRequestForm(**data)
        request.method = 'POST'
        form = EasyFormForm(self.ff1, request)()
        self.assertIn(
            '<span id="form-widgets-yes" class="radio-widget bool-field"><span class="selected-option">yes</span></span>',  # noqa
            form
        )

    def test_show_hidden_on_thankspage(self):
        self.ff1.showAll = True
        field_template = api.content.create(
            self.layer['portal'], 'File', id='easyform_default_fields.xml')
        with open(join(dirname(__file__), 'fixtures', 'hidden_form.xml')) as f:
            filecontent = NamedFile(f.read(), contentType='application/xml')
        field_template.file = filecontent

        data = {'hide': 'hello hidden'}
        request = self.LoadRequestForm(**data)
        request.method = 'POST'
        form = EasyFormForm(self.ff1, request)()
        self.assertIn(
            '<span id="form-widgets-hide" class="text-widget textline-field">hello hidden</span>',  # noqa
            form
        )

    def test_no_widget_on_thankspage_fieldset(self):
        self.ff1.showAll = True
        field_template = api.content.create(
            self.layer['portal'], 'File', id='easyform_default_fields.xml')
        with open(join(dirname(__file__),
                  'fixtures', 'fieldset_form.xml')) as f:
            filecontent = NamedFile(f.read(), contentType='application/xml')
        field_template.file = filecontent

        data = {'front': 'hello front', 'back': 'hello back'}
        request = self.LoadRequestForm(**data)
        request.method = 'POST'
        form = EasyFormForm(self.ff1, request)()
        self.assertNotIn('<input id="form-widgets-back"', form)
