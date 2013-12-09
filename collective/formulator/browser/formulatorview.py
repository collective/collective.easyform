from email import Encoders
from email.Header import Header
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.utils import formataddr
from Products.CMFCore.utils import getToolByName
from types import StringTypes
from Products.Archetypes.utils import OrderedDict


from Acquisition import aq_parent, aq_inner
from BTrees.IOBTree import IOBTree
try:
    from BTrees.LOBTree import LOBTree
    SavedDataBTree = LOBTree
except ImportError:
    SavedDataBTree = IOBTree
from BTrees.Length import Length
from DateTime import DateTime
from Products.CMFCore.Expression import getExprContext, Expression
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.PythonScript import PythonScript
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher.mapply import mapply
from copy import deepcopy
from logging import getLogger
from plone.autoform.form import AutoExtensibleForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.memoize.instance import memoize
from plone.schemaeditor.browser.field.traversal import FieldContext
from plone.schemaeditor.browser.schema.add_field import FieldAddForm
from plone.schemaeditor.browser.schema.listing import SchemaListing, SchemaListingPage
from plone.schemaeditor.browser.schema.traversal import SchemaContext
from plone.schemaeditor.interfaces import IFieldEditFormSchema, IFieldEditorExtender
from plone.schemaeditor.utils import SchemaModifiedEvent
from plone.supermodel.exportimport import BaseHandler
from plone.supermodel.parser import IFieldMetadataHandler
from plone.supermodel.utils import ns
from plone.z3cform import layout
from time import time
from z3c.form import button, form, field
from z3c.form.interfaces import DISPLAY_MODE, IErrorViewSnippet
from zope import schema as zs
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getUtilitiesFor, adapter, adapts
from zope.component import queryUtility, getAdapters, getMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, implementer
from zope.schema import getFieldsInOrder, ValidationError
from zope.schema.vocabulary import SimpleVocabulary

from collective.formulator.interfaces import (
    INewAction,
    IActionFactory,
    IFormulatorSchemaContext,
    IFormulatorActionsContext,
    IActionContext,
    IActionEditForm,
    IAction,
    IMailer,
    ICustomScript,
    ISaveData,
    IFieldExtender,
    IActionExtender,
)
from collective.formulator.api import (
    get_expression,
    get_schema,
    get_actions,
    set_schema,
    set_actions,
    get_context,
)
from collective.formulator import formulatorMessageFactory as _

logger = getLogger("collective.formulator")


class FormulatorForm(DefaultEditForm):

    """
    Formulator form
    """
    ignoreContext = True
    #method = "get"
    # def action(self):
        #""" Redefine <form action=''> attribute.
        #"""
        # return self.context.absolute_url()

    def enable_form_tabbing(self):
        return self.context.form_tabbing

    def enable_unload_protection(self):
        return self.context.unload_protection

    def enableCSRFProtection(self):
        return self.context.CSRFProtection

    @property
    def schema(self):
        schema = get_schema(self.context)
        return schema

    @property
    def additionalSchemata(self):
        return ()

    def processActions(self, errors, data):
        if not errors:
            # get a list of adapters with no duplicates, retaining order
            actions = getFieldsInOrder(get_actions(self.context))
            for name, action in actions:
                # Now, see if we should execute it.
                # Check to see if execCondition exists and has contents
                execCondition = IActionExtender(action).execCondition
                if execCondition:
                    doit = get_expression(self.context, execCondition)
                else:
                    doit = True
                if doit:
                    if hasattr(action, "onSuccess"):
                        result = action.onSuccess(data, self.request)
                        if isinstance(result, dict) and len(result):
                            # return the dict, which hopefully uses
                            # field ids or FORM_ERROR_MARKER for keys
                            return result
        return errors

    @button.buttonAndHandler(_(u'Save'), name='save', condition=lambda form: not hasattr(form, 'output'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        errors = self.processActions(errors, data)
        if errors:
            for field in errors:
                class Error(ValidationError):
                    __doc__ = errors[field]
                error = Error()
                view = getMultiAdapter(
                    (error, self.request, self.widgets[
                     field], self.widgets[field].field, self, self.context),
                    IErrorViewSnippet)
                view.update()
                self.widgets.errors += (view,)
                self.widgets[field].error = view
            self.status = self.formErrorsMessage
            return
        # self.applyChanges(data)
        thanksPageOverride = self.context.thanksPageOverride
        if thanksPageOverride:
            thanksPageOverrideAction = self.context.thanksPageOverrideAction
            expression = Expression(thanksPageOverride)
            expression_context = getExprContext(self.context)
            thanksPage = expression(expression_context)
            #import pdb; pdb.set_trace()
            if thanksPageOverrideAction == "redirect_to":
                self.request.response.redirect(thanksPage)
                return
            elif thanksPageOverrideAction == "traverse_to":
                thanksPage = self.context.restrictedTraverse(
                    thanksPage.encode("utf-8"))
                thanksPage = mapply(
                    thanksPage, self.request.args, self.request).encode("utf-8")
                self.request.response.write(thanksPage)
        self.output = data
        self.mode = DISPLAY_MODE
        for widget in self.widgets.values():
            widget.mode = DISPLAY_MODE
        for group in self.groups:
            for widget in group.widgets.values():
                widget.mode = DISPLAY_MODE
        self.updateWidgets()
        # self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u'Cancel'), name='cancel', condition=lambda form: form.context.useCancelButton)
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        view_url = self.context.absolute_url()
        return view_url

    def updateActions(self):
        super(FormulatorForm, self).updateActions()
        if 'save' in self.actions:
            self.actions['save'].title = self.context.submitLabel
        if 'cancel' in self.actions:
            self.actions['cancel'].title = self.context.resetLabel

    @property
    def label(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

#FormulatorView = layout.wrap_form(FormulatorForm, index=ViewPageTemplateFile("formulator_view.pt"))
FormulatorView = layout.wrap_form(FormulatorForm)


class FormulatorSchemaView(SchemaContext):
    implements(IFormulatorSchemaContext)
    #schemaEditorView = 'fields'

    def __init__(self, context, request):
        schema = get_schema(context)
        super(FormulatorSchemaView, self).__init__(
            schema,
            request,
            name='fields'
        )

    def browserDefault(self, request):
        """ If not traversing through the schema to a field, show the SchemaListingPage.
        """
        return self, ('@@fields',)


class ActionContext(FieldContext):

    """ wrapper for published zope 3 schema fields
    """
    implements(IActionContext)

    def publishTraverse(self, request, name):
        """ It's not valid to traverse to anything below a field context.
        """
        # hack to make inline validation work
        # (plone.app.z3cform doesn't know the form is the default view)
        if name == self.__name__:
            return EditView(self, request).__of__(self)

        return DefaultPublishTraverse(self, request).publishTraverse(request, name)


class FormulatorActionsView(SchemaContext):
    implements(IFormulatorActionsContext)
    #schemaEditorView = 'actions'

    def __init__(self, context, request):
        schema = get_actions(context)
        super(FormulatorActionsView, self).__init__(
            schema,
            request,
            name='actions'
        )

    def publishTraverse(self, request, name):
        """ Look up the field whose name matches the next URL path element, and wrap it.
        """
        try:
            return ActionContext(self.schema[name], self.request).__of__(self)
        except KeyError:
            return DefaultPublishTraverse(self, request).publishTraverse(request, name)

    def browserDefault(self, request):
        """ If not traversing through the schema to a field, show the SchemaListingPage.
        """
        return self, ('@@actions',)


def updateSchema(obj, event):
    set_schema(obj.aq_parent, obj.schema)


def updateActions(obj, event):
    set_actions(obj.aq_parent, obj.schema)


class FormulatorActionsListing(SchemaListing):
    template = ViewPageTemplateFile('actions_listing.pt')

    @memoize
    def _field_factory(self, field):
        field_identifier = u'%s.%s' % (
            field.__module__, field.__class__.__name__)
        if self.context.allowedFields is not None:
            if field_identifier not in self.context.allowedFields:
                return None
        return queryUtility(IActionFactory, name=field_identifier)

    @button.buttonAndHandler(_(u'Save'))
    def handleSaveDefaults(self, action):
        # ignore fields from behaviors by setting their widgets' modes
        # to the display mode while we extract the form values (hack!)
        widget_modes = {}
        for widget in self._iterateOverWidgets():
            if widget.field.interface is not self.context.schema:
                widget_modes[widget] = widget.mode
                widget.mode = DISPLAY_MODE

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        for fname, value in data.items():
            self.context.schema[fname].required = value
        notify(SchemaModifiedEvent(self.context))

        # restore the actual widget modes so they render a preview
        for widget, mode in widget_modes.items():
            widget.mode = mode

        # update widgets to take the new defaults into account
        self.updateWidgets()
        self.request.response.redirect(self.context.absolute_url())


class FormulatorSchemaListingPage(SchemaListingPage):

    """ Form wrapper so we can get a form with layout.

        We define an explicit subclass rather than using the wrap_form method
        from plone.z3cform.layout so that we can inject the schema name into
        the form label.
    """
    index = ViewPageTemplateFile("model_listing.pt")


class FormulatorActionsListingPage(SchemaListingPage):

    """ Form wrapper so we can get a form with layout.

        We define an explicit subclass rather than using the wrap_form method
        from plone.z3cform.layout so that we can inject the schema name into
        the form label.
    """
    form = FormulatorActionsListing
    index = ViewPageTemplateFile("model_listing.pt")


class ActionAddForm(FieldAddForm):

    fields = field.Fields(INewAction)
    label = _("Add new action")
    #id = 'add-action-form'

ActionAddFormPage = layout.wrap_form(ActionAddForm)


class ActionEditForm(AutoExtensibleForm, form.EditForm):
    implements(IActionEditForm)

    def __init__(self, context, request):
        super(form.EditForm, self).__init__(context, request)
        self.field = context.field

    def getContent(self):
        return self.field

    @lazy_property
    def schema(self):
        return IFieldEditFormSchema(self.field)

    @lazy_property
    def additionalSchemata(self):
        schema_context = self.context.aq_parent
        return [v for k, v in getAdapters((schema_context, self.field), IFieldEditorExtender)]

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # clear current min/max to avoid range errors
        if 'min' in data:
            self.field.min = None
        if 'max' in data:
            self.field.max = None

        changes = self.applyChanges(data)

        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

        notify(SchemaModifiedEvent(self.context.aq_parent))
        self.redirectToParent()

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.redirectToParent()

    def redirectToParent(self):
        parent = aq_parent(aq_inner(self.context))
        url = parent.absolute_url()
        if hasattr(parent, 'schemaEditorView') and parent.schemaEditorView:
            url += '/@@' + parent.schemaEditorView

        self.request.response.redirect(url)


class EditView(layout.FormWrapper):
    form = ActionEditForm

    def __init__(self, context, request):
        super(EditView, self).__init__(context, request)
        self.field = context.field

    @lazy_property
    def label(self):
        return _(u"Edit Field '${fieldname}'", mapping={'fieldname': self.field.__name__})


def FormulatorActionsVocabularyFactory(context):
    field_factories = getUtilitiesFor(IActionFactory)
    terms = []
    for (id, factory) in field_factories:
        terms.append(SimpleVocabulary.createTerm(
            factory, translate(factory.title), factory.title))
    return SimpleVocabulary(terms)


class ActionFactory(object):
    implements(IActionFactory)

    title = u''

    def __init__(self, fieldcls, title, *args, **kw):
        self.fieldcls = fieldcls
        self.title = title
        self.args = args
        self.kw = kw

    def __call__(self, *args, **kw):
        kwargs = deepcopy(self.kw)
        kwargs.update(**kw)
        return self.fieldcls(*(self.args + args), **kwargs)


class Action(zs.Bool):

    """ Base action class """

    def onSuccess(self, fields, request):
        raise NotImplementedError(
            "There is not implemented 'onSuccess' of %r" % (self,))


@implementer(IMailer)
class Mailer(Action):
    __doc__ = IMailer.__doc__

    def __init__(self, **kw):
        for i, f in IMailer.namesAndDescriptions():
            setattr(self, i, kw.pop(i, None) or f.default)
        super(Mailer, self).__init__(**kw)

    def secure_header_line(self, line):
        nlpos = line.find('\x0a')
        if nlpos >= 0:
            line = line[:nlpos]
        nlpos = line.find('\x0d')
        if nlpos >= 0:
            line = line[:nlpos]
        return line

    def _destFormat(self, input):
        """ Format destination (To) input.
            Input may be a string or sequence of strings;
            returns a well-formatted address field
        """

        if type(input) in StringTypes:
            input = [s for s in input.split(',')]
        input = [s for s in input if s]
        filtered_input = [s.strip().encode('utf-8') for s in input]

        if filtered_input:
            return "<%s>" % '>, <'.join(filtered_input)
        else:
            return ''

    def get_mail_body(self, fields, request, **kwargs):
        """Returns the mail-body with footer.
        """

        all_fields = [f for f in fields
                      # TODO
                      # if not (f.isLabel() or f.isFileField()) and not (getattr(self,
                      # 'showAll', True) and f.getServerSide())]
                      ]

        # which fields should we show?
        if getattr(self, 'showAll', True):
            live_fields = all_fields
        else:
            live_fields = \
                [f for f in all_fields
                 if f in getattr(self, 'showFields', ())]

        if not getattr(self, 'includeEmpties', True):
            all_fields = live_fields
            live_fields = []
            for f in all_fields:
                value = fields[f]
                if value and value != 'No Input':
                    live_fields.append(f)

        #context = get_context(self)
        #schema = get_schema(context)
        #bare_fields = [schema[f] for f in live_fields]
        bodyfield = self.body_pt

        # pass both the bare_fields (fgFields only) and full fields.
        # bare_fields for compatability with older templates,
        # full fields to enable access to htmlValue
        #body = bodyfield.get(self, fields=bare_fields, wrappedFields=live_fields, **kwargs)
        body = bodyfield

        # if isinstance(body, unicode):
            #body = body.encode("utf-8")

        #keyid = getattr(self, 'gpg_keyid', None)
        #encryption = gpg and keyid

        # if encryption:
            #bodygpg = gpg.encrypt(body, keyid)
            # if bodygpg.strip():
                #body = bodygpg

        return body

    def get_header_body_tuple(self, fields, request,
                              from_addr=None, to_addr=None,
                              subject=None, **kwargs):
        """Return header and body of e-mail as an 3-tuple:
        (header, additional_header, body)

        header is a dictionary, additional header is a list, body is a StringIO

        Keyword arguments:
        request -- (optional) alternate request object to use
        """
        context = get_context(self)
        pprops = getToolByName(context, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        pms = getToolByName(context, 'portal_membership')
        utils = getToolByName(context, 'plone_utils')

        body = self.get_mail_body(fields, request, **kwargs)

        # fields = self.fgFields()

        # get Reply-To
        reply_addr = None
        if hasattr(self, 'replyto_field'):
            reply_addr = request.form.get(self.replyto_field, None)

        # get subject header
        nosubject = '(no subject)'
        if hasattr(self, 'subjectOverride') and self.subjectOverride and get_expression(context, self.subjectOverride):
            # subject has a TALES override
            subject = get_expression(context, self.subjectOverride).strip()
        else:
            subject = getattr(self, 'msg_subject', nosubject)
            subjectField = request.form.get(self.subject_field, None)
            if subjectField is not None:
                subject = subjectField
            else:
                # we only do subject expansion if there's no field chosen
                #subject = self._dreplace(subject)
                subject = subject

        # Get From address
        if hasattr(self, 'senderOverride') and self.senderOverride and get_expression(context, self.senderOverride):
            from_addr = get_expression(context, self.senderOverride).strip()
        else:
            from_addr = from_addr or site_props.getProperty('email_from_address') or \
                portal.getProperty('email_from_address')

        # Get To address and full name
        if hasattr(self, 'recipientOverride') and self.recipientOverride and get_expression(context, self.recipientOverride):
            recip_email = get_expression(context, self.recipientOverride)
        else:
            recip_email = None
            if hasattr(self, 'to_field') and self.to_field:
                recip_email = request.form.get(self.to_field, None)
            if not recip_email:
                recip_email = self.recipient_email

        recip_email = self._destFormat(recip_email)

        recip_name = self.recipient_name.encode('utf-8')

        # if no to_addr and no recip_email specified, use owner adress if possible.
        # if not, fall back to portal email_from_address.
        # if still no destination, raise an assertion exception.
        if not recip_email and not to_addr:
            ownerinfo = context.getOwner()
            ownerid = ownerinfo.getId()
            fullname = ownerid
            userdest = pms.getMemberById(ownerid)
            if userdest is not None:
                fullname = userdest.getProperty('fullname', ownerid)
            toemail = ''
            if userdest is not None:
                toemail = userdest.getProperty('email', '')
            if not toemail:
                toemail = portal.getProperty('email_from_address')
            assert toemail, """
                    Unable to mail form input because no recipient address has been specified.
                    Please check the recipient settings of the PloneFormGen "Mailer" within the
                    current form folder.
                """
            to = formataddr((fullname, toemail))
        else:
            to = to_addr or '%s %s' % (recip_name, recip_email)

        headerinfo = OrderedDict()

        headerinfo['To'] = self.secure_header_line(to)
        headerinfo['From'] = self.secure_header_line(from_addr)
        if reply_addr:
            headerinfo['Reply-To'] = self.secure_header_line(reply_addr)

        # transform subject into mail header encoded string
        email_charset = portal.getProperty('email_charset', 'utf-8')

        if not isinstance(subject, unicode):
            site_charset = utils.getSiteEncoding()
            subject = unicode(subject, site_charset, 'replace')

        msgSubject = self.secure_header_line(
            subject).encode(email_charset, 'replace')
        msgSubject = str(Header(msgSubject, email_charset))
        headerinfo['Subject'] = msgSubject

        # CC
        cc_recips = filter(None, self.cc_recipients)
        if hasattr(self, 'ccOverride') and self.ccOverride and get_expression(context, self.ccOverride):
            cc_recips = get_expression(context, self.ccOverride)
        if cc_recips:
            headerinfo['Cc'] = self._destFormat(cc_recips)

        # BCC
        bcc_recips = filter(None, self.bcc_recipients)
        if hasattr(self, 'bccOverride') and self.bccOverride and get_expression(context, self.bccOverride):
            bcc_recips = get_expression(context, self.bccOverride)
        if bcc_recips:
            headerinfo['Bcc'] = self._destFormat(bcc_recips)

        for key in getattr(self, 'xinfo_headers', []):
            headerinfo['X-%s' % key] = self.secure_header_line(
                request.get(key, 'MISSING'))

        # return 3-Tuple
        return (headerinfo, self.additional_headers or [], body)

    def get_mail_text(self, fields, request):
        """Get header and body of e-mail as text (string)
        """

        (headerinfo, additional_headers,
         body) = self.get_header_body_tuple(fields, request)

        if not isinstance(body, unicode):
            body = unicode(body, 'UTF-8')
        email_charset = 'utf-8'
        # always use text/plain for encrypted bodies
        subtype = getattr(
            self, 'gpg_keyid', False) and 'plain' or self.body_type or 'html'
        mime_text = MIMEText(body.encode(email_charset, 'replace'),
                             _subtype=subtype, _charset=email_charset)

        #attachments = self.get_attachments(fields, request)
        attachments = []

        if attachments:
            outer = MIMEMultipart()
            outer.attach(mime_text)
        else:
            outer = mime_text

        # write header
        for key, value in headerinfo.items():
            outer[key] = value

        # write additional header
        for a in additional_headers:
            key, value = a.split(':', 1)
            outer.add_header(key, value.strip())

        for attachment in attachments:
            filename = attachment[0]
            ctype = attachment[1]
            # encoding = attachment[2]
            content = attachment[3]

            if ctype is None:
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1)

            if maintype == 'text':
                msg = MIMEText(content, _subtype=subtype)
            elif maintype == 'image':
                msg = MIMEImage(content, _subtype=subtype)
            elif maintype == 'audio':
                msg = MIMEAudio(content, _subtype=subtype)
            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(content)
                # Encode the payload using Base64
                Encoders.encode_base64(msg)

            # Set the filename parameter
            msg.add_header(
                'Content-Disposition', 'attachment', filename=filename)
            outer.attach(msg)

        return outer.as_string()

    def onSuccess(self, fields, request):
        """
        e-mails data.
        """
        context = get_context(self)
        mailtext = self.get_mail_text(fields, request)
        host = context.MailHost
        host.send(mailtext)


@implementer(ICustomScript)
class CustomScript(Action):
    __doc__ = ICustomScript.__doc__

    def __init__(self, **kw):
        for i, f in ICustomScript.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
        super(CustomScript, self).__init__(**kw)

    def getScript(self, context):
        # Generate Python script object

        body = self.ScriptBody
        role = self.ProxyRole
        script = PythonScript(self.__name__)
        script = script.__of__(context)

        # Force proxy role
        if role != u"none":
            script.manage_proxy((role,))

        script.ZPythonScript_edit(
            "fields, ploneformgen, request", body.encode("utf-8"))
        return script

    def sanifyFields(self, form):
        # Makes request.form fields accessible in a script
        #
        # Avoid Unauthorized exceptions since request.form is inaccesible

        result = {}
        for field in form:
            result[field] = form[field]
        return result

    def checkWarningsAndErrors(self, script):
        # Raise exception if there has been bad things with the script
        # compiling

        if len(script.warnings) > 0:
            logger.warn("Python script " + self.title_or_id()
                        + " has warning:" + str(script.warnings))

        if len(script.errors) > 0:
            logger.error("Python script " + self.title_or_id()
                         + " has errors: " + str(script.errors))
            raise ValueError(
                "Python script " + self.title_or_id() + " has errors: " + str(script.errors))

    def executeCustomScript(self, result, form, req):
        # Execute in-place script

        # @param result Extracted fields from request.form
        # @param form PloneFormGen object

        script = self.getScript(form)
        self.checkWarningsAndErrors(script)
        response = script(result, form, req)
        return response

    def onSuccess(self, fields, request):
        # Executes the custom script
        form = get_context(self)
        resultData = self.sanifyFields(request.form)
        return self.executeCustomScript(resultData, form, request)


@implementer(ISaveData)
class SaveData(Action):
    __doc__ = ISaveData.__doc__

    def __init__(self, **kw):
        for i, f in ISaveData.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
        super(SaveData, self).__init__(**kw)

    def _migrateStorage(self, context):
        updated = \
            hasattr(context, '_inputStorage') and \
            hasattr(context, '_inputItems') and \
            hasattr(context, '_length')

        if not updated:
            context._inputStorage = SavedDataBTree()
            context._inputItems = 0
            context._length = Length()

    def _addDataRow(self, value):

        context = get_context(self)
        self._migrateStorage(context)

        if isinstance(context._inputStorage, IOBTree):
            # 32-bit IOBTree; use a key which is more likely to conflict
            # but which won't overflow the key's bits
            id = context._inputItems
            context._inputItems += 1
        else:
            # 64-bit LOBTree
            id = int(time() * 1000)
            while id in context._inputStorage:  # avoid collisions during testing
                id += 1
        context._inputStorage[id] = value
        context._length.change(1)

    def onSuccess(self, fields, request):
        """
        saves data.
        """
        # if LP_SAVE_TO_CANONICAL and not loopstop:
            # LinguaPlone functionality:
            # check to see if we're in a translated
            # form folder, but not the canonical version.
            #parent = self.aq_parent
            # if safe_hasattr(parent, 'isTranslation') and \
               # parent.isTranslation() and not parent.isCanonical():
                # look in the canonical version to see if there is
                # a matching (by id) save-data adapter.
                # If so, call its onSuccess method
                #cf = parent.getCanonical()
                #target = cf.get(self.getId())
                # if target is not None and target.meta_type == 'FormSaveDataAdapter':
                    #target.onSuccess(fields, request, loopstop=True)
                    # return

        #from ZPublisher.HTTPRequest import FileUpload

        data = []
        for f in fields:
            showFields = getattr(self, 'showFields', [])
            if showFields and f not in showFields:
                continue
            # if f.isFileField():
                #file = request.form.get('%s_file' % f.fgField.getName())
                # if isinstance(file, FileUpload) and file.filename != '':
                    # file.seek(0)
                    #fdata = file.read()
                    #filename = file.filename
                    #mimetype, enc = guess_content_type(filename, fdata, None)
                    # if mimetype.find('text/') >= 0:
                        # convert to native eols
                        # fdata = fdata.replace('\x0d\x0a', '\n').replace(
                            #'\x0a', '\n').replace('\x0d', '\n')
                        # data.append('%s:%s:%s:%s' %
                                    #(filename, mimetype, enc, fdata))
                    # else:
                        # data.append('%s:%s:%s:Binary upload discarded' %
                                    #(filename, mimetype, enc))
                # else:
                    #data.append('NO UPLOAD')
            # elif not f.isLabel():
                #val = request.form.get(f.fgField.getName(), '')
                # if not type(val) in StringTypes:
                    # Zope has marshalled the field into
                    # something other than a string
                    #val = str(val)
                # data.append(val)
            data.append(fields[f])

        if self.ExtraData:
            for f in self.ExtraData:
                if f == 'dt':
                    data.append(str(DateTime()))
                else:
                    data.append(getattr(request, f, ''))

        self._addDataRow(data)


MailerAction = ActionFactory(
    Mailer, _(u'label_mailer_action', default=u'Mailer'))
CustomScriptAction = ActionFactory(
    CustomScript, _(u'label_customscript_action', default=u'CustomScript'))
SaveDataAction = ActionFactory(
    SaveData, _(u'label_savedata_action', default=u'SaveData'))

MailerHandler = BaseHandler(Mailer)
CustomScriptHandler = BaseHandler(CustomScript)
SaveDataHandler = BaseHandler(SaveData)


@adapter(IFormulatorSchemaContext, zs.interfaces.IField)
def get_field_extender(context, field):
    return IFieldExtender


def _get_(self, key):
    return self.field.interface.queryTaggedValue(key, {}).get(self.field.__name__)


def _set_(self, value, key):
    data = self.field.interface.queryTaggedValue(key, {})
    data[self.field.__name__] = value
    self.field.interface.setTaggedValue(key, data)


class FieldExtender(object):
    implements(IFieldExtender)
    adapts(zs.interfaces.IField)

    def __init__(self, field):
        self.field = field

    TDefault = property(lambda x: _get_(x, 'TDefault'),
                        lambda x, value: _set_(x, value, 'TDefault'))
    TEnabled = property(lambda x: _get_(x, 'TEnabled'),
                        lambda x, value: _set_(x, value, 'TEnabled'))
    TValidator = property(lambda x: _get_(x, 'TValidator'),
                          lambda x, value: _set_(x, value, 'TValidator'))
    serverSide = property(lambda x: _get_(x, 'serverSide'),
                          lambda x, value: _set_(x, value, 'serverSide'))


class FormulatorFieldMetadataHandler(object):

    """Support the formulator: namespace in model definitions.
    """
    implements(IFieldMetadataHandler)

    namespace = 'http://namespaces.plone.org/supermodel/formulator'
    prefix = 'formulator'

    def read(self, fieldNode, schema, field):
        name = field.__name__
        for i in ['TDefault', 'TEnabled', 'TValidator']:
            value = fieldNode.get(ns(i, self.namespace))
            data = schema.queryTaggedValue(i, {})
            if value:
                data[name] = value
                schema.setTaggedValue(i, data)
        # serverSide
        value = fieldNode.get(ns('serverSide', self.namespace))
        data = schema.queryTaggedValue('serverSide', {})
        if value:
            # TODO eval
            data[name] = eval(value)
            schema.setTaggedValue('serverSide', data)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        for i in ['TDefault', 'TEnabled', 'TValidator']:
            value = schema.queryTaggedValue(i, {}).get(name, None)
            if value:
                fieldNode.set(ns(i, self.namespace), value)
        # serverSide
        value = schema.queryTaggedValue('serverSide', {}).get(name, None)
        if isinstance(value, bool):
            fieldNode.set(ns('serverSide', self.namespace), str(value))


@adapter(IFormulatorActionsContext, IAction)
def get_action_extender(context, action):
    return IActionExtender


class ActionExtender(object):
    implements(IActionExtender)
    adapts(IAction)

    def __init__(self, field):
        self.field = field

    execCondition = property(lambda x: _get_(x, 'execCondition'),
                             lambda x, value: _set_(x, value, 'execCondition'))


class FormulatorActionMetadataHandler(object):

    """Support the formulator: namespace in model definitions.
    """
    implements(IFieldMetadataHandler)

    namespace = 'http://namespaces.plone.org/supermodel/formulator'
    prefix = 'formulator'

    def read(self, fieldNode, schema, field):
        name = field.__name__
        value = fieldNode.get(ns('execCondition', self.namespace))
        data = schema.queryTaggedValue('execCondition', {})
        if value:
            data[name] = value
            schema.setTaggedValue('execCondition', data)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        value = schema.queryTaggedValue('execCondition', {}).get(name, None)
        if value:
            fieldNode.set(ns('execCondition', self.namespace), value)
