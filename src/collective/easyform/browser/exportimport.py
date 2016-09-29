# -*- coding: utf-8 -*-

from collective.easyform import easyformMessageFactory as _
from collective.easyform.interfaces import IEasyFormImportFormSchema
from datetime import datetime
from plone.z3cform import layout
from Products.Five import BrowserView
from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.context import TarballImportContext
from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getMultiAdapter


class EasyFormExportView(BrowserView):

    """See ..interfaces.exportimport.IEasyFormExportView
    """

    def __call__(self):
        """See ..interfaces.exportimport.IEasyFormExportView.__call__
        """
        ctx = TarballExportContext(self.context)
        response = self.request.RESPONSE
        disposition = 'attachment; filename="{0}-{1:{2}}.tar.gz"'.format(
            self.context.getId(), datetime.now(), '%Y%m%d%H%M%S')

        response.setHeader('Content-type', 'application/x-gzip')
        response.setHeader('Content-disposition', disposition)

        # export the structure treating the current form as our root context
        IFilesystemExporter(self.context).export(ctx, 'structure', True)

        return ctx.getArchive()


class EasyFormImportForm(form.Form):

    """The form class for importing of exported easyforms
    """
    fields = field.Fields(IEasyFormImportFormSchema)
    ignoreContext = True
    ignoreReadonly = True

    @button.buttonAndHandler(_(u'import'), name='import')
    def handleImport(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        ctx = TarballImportContext(self.context, data['upload'])
        IFilesystemImporter(self.context).import_(ctx, 'structure', True)

        self.status = _(u'Form imported.')
        IStatusMessage(self.request).addStatusMessage(self.status, type='info')

        url = getMultiAdapter(
            (self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)


EasyFormImportView = layout.wrap_form(EasyFormImportForm)
