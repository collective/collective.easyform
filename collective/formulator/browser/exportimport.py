from zope.interface import implements
from zope.formlib import form
from zope.component import getMultiAdapter

from Products.Five import BrowserView
try:
    from Products.Five.formlib import formbase
except:  # Zope2.13 compatibility
    from five.formlib import formbase

from Products.statusmessages.interfaces import IStatusMessage

from collective.formulator.interfaces import IFormulatorImportFormSchema
from collective.formulator import formulatorMessageFactory as _

from Products.GenericSetup.context import TarballExportContext, TarballImportContext
from Products.GenericSetup.interfaces import IFilesystemExporter, IFilesystemImporter

try:
    from plone.dexterity.exportimport import DexterityContentExporterImporter
    has_export = True
except ImportError:
    has_export = False


class FormulatorExportView(BrowserView):

    """See ..interfaces.exportimport.IFormulatorExportView
    """

    def __call__(self):
        """See ..interfaces.exportimport.IFormulatorExportView.__call__
        """
        if not has_export:
            return
        ctx = TarballExportContext(self.context)

        self.request.RESPONSE.setHeader('Content-type', 'application/x-gzip')
        self.request.RESPONSE.setHeader('Content-disposition',
                                        'attachment; filename=%s' % ctx.getArchiveFilename())

        # export the structure treating the current form as our root context
        IFilesystemExporter(self.context).export(ctx, 'structure', True)

        return ctx.getArchive()


class FormulatorImportView(formbase.Form):

    """The formlib class for importing of exported formulators
    """
    form_fields = form.Fields(IFormulatorImportFormSchema)
    status = errors = None
    prefix = 'form'

    @form.action(_(u"import"))
    def action_import(self, action, data):
        if not has_export:
            return

        ctx = TarballImportContext(self.context, data['upload'])
        IFilesystemImporter(self.context).import_(ctx, 'structure', True)

        message = _(u'Form imported.')
        IStatusMessage(self.request).addStatusMessage(message, type='info')

        url = getMultiAdapter(
            (self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)

        return ''
