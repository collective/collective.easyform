from AccessControl import getSecurityManager
from BTrees.IOBTree import IOBTree
try:
    from BTrees.LOBTree import LOBTree
    SavedDataBTree = LOBTree
except ImportError:
    SavedDataBTree = IOBTree
from DateTime import DateTime
from Products.Archetypes.utils import OrderedDict
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PythonScripts.PythonScript import PythonScript
from ZPublisher.mapply import mapply
from copy import deepcopy
from email import Encoders
from email.Header import Header
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.utils import formataddr
from logging import getLogger
from plone.autoform.form import AutoExtensibleForm
from plone.namedfile.interfaces import INamedFile
from plone.supermodel.exportimport import BaseHandler
from plone.supermodel.parser import IFieldMetadataHandler
from plone.supermodel.utils import ns
from plone.z3cform import layout
from time import time
from types import StringTypes
from z3c.form import button, form, validator
from z3c.form.interfaces import DISPLAY_MODE, IErrorViewSnippet, IValidator, IValue
from zope import schema as zs
from zope.component import getUtilitiesFor, adapter, adapts
from zope.component import queryUtility, getMultiAdapter
from zope.contenttype import guess_content_type
from zope.i18n import translate
from zope.interface import implements, Invalid, Interface
from zope.schema import getFieldsInOrder, ValidationError
from zope.schema.vocabulary import SimpleVocabulary

from collective.formulator.interfaces import (
    IAction,
    IActionExtender,
    IActionFactory,
    ICustomScript,
    IFieldExtender,
    IFormulator,
    IFormulatorActionsContext,
    IFormulatorFieldsContext,
    IMailer,
    ISaveData,
)
from collective.formulator.api import (
    DollarVarReplacer,
    get_actions,
    get_context,
    get_expression,
    get_fields,
)
from collective.formulator.validators import IFieldValidator
from collective.formulator import formulatorMessageFactory as _

logger = getLogger("collective.formulator")


class FormulatorForm(AutoExtensibleForm, form.Form):

    """
    Formulator form
    """
    template = ViewPageTemplateFile('formulator_form.pt')
    ignoreContext = True
    css_class = 'formulatorForm'
    thanksPage = False
    # method = "get"

    @property
    def default_fieldset_label(self):
        return self.context.default_fieldset_label or super(FormulatorForm, self).default_fieldset_label

    def action(self):
        """ Redefine <form action=''> attribute.
        """
        action = getattr(self.context, 'formActionOverride')
        if action:
            action = get_expression(self.context, action)
        if not action:
            action = self.context.absolute_url()
        if self.context.forceSSL:
            action = action.replace('http://', 'https://')
        return action

    @property
    def enable_form_tabbing(self):
        return self.context.form_tabbing

    @property
    def enable_unload_protection(self):
        return self.context.unload_protection

    @property
    def enableCSRFProtection(self):
        return self.context.CSRFProtection

    @property
    def label(self):
        return self.thanksPage and self.context.thankstitle or self.context.Title()

    @property
    def description(self):
        return self.thanksPage and self.context.thanksdescription or self.context.Description()

    @property
    def prologue(self):
        return self.thanksPage and self.thanksPrologue or self.context.formPrologue.output

    @property
    def epilogue(self):
        return self.thanksPage and self.thanksEpilogue or self.context.formEpilogue.output

    @property
    def schema(self):
        return get_fields(self.context)

    def updateServerSideData(self, data):
        for fname in self.schema:
            field = self.schema[fname]
            efield = IFieldExtender(field)
            serverSide = getattr(efield, 'serverSide', False)
            if not serverSide:
                continue
            fdefault = field.default
            TDefault = getattr(efield, 'TDefault', None)
            value = get_expression(
                self.context, TDefault) if TDefault else fdefault
            data[fname] = value
        return data

    def processActions(self, data):
        # get a list of adapters with no duplicates, retaining order
        actions = getFieldsInOrder(get_actions(self.context))
        for name, action in actions:
            if not action.required:
                continue
            # Now, see if we should execute it.
            # Check to see if execCondition exists and has contents
            execCondition = IActionExtender(action).execCondition
            if execCondition:
                doit = get_expression(self.context, execCondition)
            else:
                doit = True
            if doit and hasattr(action, "onSuccess"):
                result = action.onSuccess(data, self.request)
                if isinstance(result, dict) and len(result):
                    # return the dict, which hopefully uses
                    # field ids or FORM_ERROR_MARKER for keys
                    return result

    def setDisplayMode(self, mode):
        self.mode = mode
        for widget in self.widgets.values():
            widget.mode = mode
        self.updateWidgets()
        for group in self.groups:
            group.widgets.mode = mode
            for field in group.widgets:
                del group.widgets[field]
            group.widgets.update()

    def setErrorsMessage(self, errors):
        for field in errors:
            if field not in self.widgets:
                continue
            error = ValidationError()
            error.doc = lambda: errors[field]
            view = getMultiAdapter(
                (error, self.request, self.widgets[
                    field], self.widgets[field].field, self, self.context),
                IErrorViewSnippet)
            view.update()
            self.widgets.errors += (view,)
            self.widgets[field].error = view
        self.status = self.formErrorsMessage

    @button.buttonAndHandler(_(u'Submit'), name='submit', condition=lambda form: not form.thanksPage)
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        data = self.updateServerSideData(data)
        errors = self.processActions(data)
        if errors:
            return self.setErrorsMessage(errors)
        thanksPageOverride = self.context.thanksPageOverride
        if thanksPageOverride:
            thanksPageOverrideAction = self.context.thanksPageOverrideAction
            thanksPage = get_expression(self.context, thanksPageOverride)
            if thanksPageOverrideAction == "redirect_to":
                self.request.response.redirect(thanksPage)
            elif thanksPageOverrideAction == "traverse_to":
                thanksPage = self.context.restrictedTraverse(
                    thanksPage.encode("utf-8"))
                thanksPage = mapply(
                    thanksPage, self.request.args, self.request).encode("utf-8")
                self.request.response.write(thanksPage)
        else:
            self.thanksPage = True
            replacer = DollarVarReplacer(data).sub
            self.thanksPrologue = self.context.thanksPrologue and replacer(
                self.context.thanksPrologue.output)
            self.thanksEpilogue = self.context.thanksEpilogue and replacer(
                self.context.thanksEpilogue.output)
            if not self.context.showAll:
                self.fields = self.setThanksFields(self.base_fields)
                for group in self.groups:
                    group.fields = self.setThanksFields(
                        self.base_groups.get(group.label))
            self.setDisplayMode(DISPLAY_MODE)
            self.updateActions()

    @button.buttonAndHandler(_(u'Reset'), name='reset', condition=lambda form: form.context.useCancelButton or form.thanksPage)
    def handleReset(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return self.context.absolute_url()

    def setOmitFields(self, fields):
        omit = []
        for fname in fields:
            field = fields[fname].field
            efield = IFieldExtender(field)
            TEnabled = getattr(efield, 'TEnabled', None)
            serverSide = getattr(efield, 'serverSide', False)
            if TEnabled and not get_expression(self.context, TEnabled) or serverSide:
                omit.append(fname)
        if omit:
            fields = fields.omit(*omit)
        return fields

    def setThanksFields(self, fields):
        showFields = self.context.showFields
        omit = [fname for fname in fields if fname not in showFields]
        if omit:
            fields = fields.omit(*omit)
        return fields

    def updateFields(self):
        super(FormulatorForm, self).updateFields()
        if not hasattr(self, 'base_fields'):
            self.base_fields = self.fields
        if not hasattr(self, 'base_groups'):
            self.base_groups = dict([(i.label, i.fields) for i in self.groups])
        self.fields = self.setOmitFields(self.base_fields)
        for group in self.groups:
            group.fields = self.setOmitFields(
                self.base_groups.get(group.label))

    def updateActions(self):
        super(FormulatorForm, self).updateActions()
        if 'submit' in self.actions:
            if self.context.submitLabelOverride:
                self.actions['submit'].title = get_expression(
                    self.context, self.context.submitLabelOverride)
            else:
                self.actions['submit'].title = self.context.submitLabel
        if 'reset' in self.actions:
            self.actions['reset'].title = self.context.resetLabel

    def formMaybeForceSSL(self):
        """ Redirect to an https:// URL if the 'force SSL' option is on.

            However, don't do so for those with rights to edit the form,
            to avoid making the form uneditable if SSL isn't configured
            properly.  These users will still get an SSL-ified form
            action for when the form is submitted.
        """
        if self.context.forceSSL and not getSecurityManager().checkPermission("cmf.ModifyPortalContent", self):
            # Make sure we're being accessed via a secure connection
            if self.request['SERVER_URL'].startswith('http://'):
                secure_url = self.request['URL'].replace('http://', 'https://')
                self.request.response.redirect(
                    secure_url, status="movedtemporarily")

    def update(self):
        '''See interfaces.IForm'''
        self.formMaybeForceSSL()
        super(FormulatorForm, self).update()

#FormulatorView = layout.wrap_form(FormulatorForm, index=ViewPageTemplateFile("formulator_view.pt"))
FormulatorView = layout.wrap_form(FormulatorForm)


class FormulatorFormEmbedded(FormulatorForm):

    """
    Formulator form embedded
    """
    template = ViewPageTemplateFile('formulator_form_embedded.pt')


class FieldExtenderValidator(validator.SimpleFieldValidator):

    """ z3c.form validator class for formulator fields """
    implements(IValidator)
    adapts(IFormulator, Interface, FormulatorForm,
           zs.interfaces.IField, Interface)

    def validate(self, value):
        """ Validate field by TValidator """
        super(FieldExtenderValidator, self).validate(value)
        efield = IFieldExtender(self.field)
        validators = getattr(efield, 'validators', [])
        if validators:
            for validator in validators:
                vmethod = queryUtility(IFieldValidator, name=validator)
                if not vmethod:
                    continue
                res = vmethod(value)
                if res:
                    raise Invalid(res)
        TValidator = getattr(efield, 'TValidator', None)
        if TValidator:
            try:
                cerr = get_expression(self.context, TValidator, value=value)
            except Exception as e:
                raise Invalid(e)
            if cerr:
                raise Invalid(cerr)


class FieldExtenderDefault(object):

    """ z3c.form default class for formulator fields """
    implements(IValue)
    adapts(IFormulator, Interface, FormulatorForm,
           zs.interfaces.IField, Interface)

    def __init__(self, context, request, view, field, widget):
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def get(self):
        """ get default value of field from TDefault """
        fdefault = self.field.default
        efield = IFieldExtender(self.field)
        TDefault = getattr(efield, 'TDefault', None)
        return get_expression(self.context, TDefault) if TDefault else fdefault


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

    def editable(self, field):
        """ test whether a given instance of a field is editable """
        return True

    def __call__(self, *args, **kw):
        kwargs = deepcopy(self.kw)
        kwargs.update(**kw)
        return self.fieldcls(*(self.args + args), **kwargs)


class Action(zs.Bool):

    """ Base action class """

    def onSuccess(self, fields, request):
        raise NotImplementedError(
            "There is not implemented 'onSuccess' of %r" % (self,))


class Mailer(Action):
    implements(IMailer)
    __doc__ = IMailer.__doc__

    def __init__(self, **kw):
        for i, f in IMailer.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
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

        context = get_context(self)
        schema = get_fields(context)
        all_fields = [f for f in fields
                      # TODO
                      # if not (f.isLabel() or f.isFileField()) and not (getattr(self,
                      # 'showAll', True) and f.getServerSide())]
                      if not (INamedFile.providedBy(fields[f])) and not (getattr(self, 'showAll', True) and IFieldExtender(schema[f]).serverSide)
                      ]

        # which fields should we show?
        if getattr(self, 'showAll', True):
            live_fields = all_fields
        else:
            live_fields = [
                f for f in all_fields if f in getattr(self, 'showFields', ())]

        if not getattr(self, 'includeEmpties', True):
            all_fields = live_fields
            live_fields = [f for f in all_fields if fields[f]]
            for f in all_fields:
                value = fields[f]
                if value:
                    live_fields.append(f)

        #bare_fields = [schema[f] for f in live_fields]
        bare_fields = dict([(f, fields[f]) for f in live_fields])
        bodyfield = self.body_pt

        # pass both the bare_fields (fgFields only) and full fields.
        # bare_fields for compatability with older templates,
        # full fields to enable access to htmlValue
        replacer = DollarVarReplacer(fields).sub
        extra = {
            'data': bare_fields,
            'fields': dict([(i, j.title) for i, j in getFieldsInOrder(schema)]),
            'mailer': self,
            'body_pre': self.body_pre and replacer(self.body_pre),
            'body_post': self.body_post and replacer(self.body_post),
            'body_footer': self.body_footer and replacer(self.body_footer),
        }
        template = ZopePageTemplate(self.__name__)
        template.write(bodyfield)
        template = template.__of__(context)
        body = template.pt_render(extra_context=extra)

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
                subject = DollarVarReplacer(fields).sub(subject)

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
                    Please check the recipient settings of the Formulator "Mailer" within the
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

    def get_attachments(self, fields, request):
        """Return all attachments uploaded in form.
        """

        attachments = []

        for fname in fields:
            field = fields[fname]
            if INamedFile.providedBy(field) and (getattr(self, 'showAll', True) or fname in getattr(self, 'showFields', ())):
                data = field.data
                filename = field.filename
                mimetype, enc = guess_content_type(filename, data, None)
                attachments.append((filename, mimetype, enc, data))
        return attachments

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

        attachments = self.get_attachments(fields, request)

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


class CustomScript(Action):
    implements(ICustomScript)
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

        # Skip check roles
        script._validateProxy = lambda i=None: None

        # Force proxy role
        if role != u"none":
            script.manage_proxy((role,))

        body = body.encode("utf-8")
        params = "fields, formulator, request"
        script.ZPythonScript_edit(params, body)
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
            logger.warn("Python script " + self.__name__
                        + " has warning:" + str(script.warnings))

        if len(script.errors) > 0:
            logger.error("Python script " + self.__name__
                         + " has errors: " + str(script.errors))
            raise ValueError(
                "Python script " + self.__name__ + " has errors: " + str(script.errors))

    def executeCustomScript(self, result, form, req):
        # Execute in-place script

        # @param result Extracted fields from request.form
        # @param form Formulator object

        script = self.getScript(form)
        self.checkWarningsAndErrors(script)
        response = script(result, form, req)
        return response

    def onSuccess(self, fields, request):
        # Executes the custom script
        form = get_context(self)
        resultData = self.sanifyFields(request.form)
        return self.executeCustomScript(resultData, form, request)


class SaveData(Action):
    implements(ISaveData)
    __doc__ = ISaveData.__doc__

    def __init__(self, **kw):
        for i, f in ISaveData.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
        super(SaveData, self).__init__(**kw)

    @property
    def _storage(self):
        context = get_context(self)
        if not hasattr(context, '_inputStorage'):
            context._inputStorage = {}
        if not self.__name__ in context._inputStorage:
            context._inputStorage[self.__name__] = SavedDataBTree()
        return context._inputStorage[self.__name__]

    def _addDataRow(self, value):
        storage = self._storage
        if isinstance(storage, IOBTree):
            # 32-bit IOBTree; use a key which is more likely to conflict
            # but which won't overflow the key's bits
            id = storage.maxKey() + 1
        else:
            # 64-bit LOBTree
            id = int(time() * 1000)
            while id in storage:  # avoid collisions during testing
                id += 1
        value['id'] = id
        storage[id] = value

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
        data = {}
        for f in fields:
            showFields = getattr(self, 'showFields', [])
            if showFields and f not in showFields:
                continue
            # data.append(fields[f])
            data[f] = fields[f]

        if self.ExtraData:
            for f in self.ExtraData:
                if f == 'dt':
                    # data.append(str(DateTime()))
                    data[f] = str(DateTime())
                else:
                    #data.append(getattr(request, f, ''))
                    data[f] = getattr(request, f, '')

        self._addDataRow(data)


MailerAction = ActionFactory(
    Mailer, _(u'label_mailer_action', default=u'Mailer'))
CustomScriptAction = ActionFactory(
    CustomScript, _(u'label_customscript_action', default=u'Custom Script'))
SaveDataAction = ActionFactory(
    SaveData, _(u'label_savedata_action', default=u'Save Data'))

MailerHandler = BaseHandler(Mailer)
CustomScriptHandler = BaseHandler(CustomScript)
SaveDataHandler = BaseHandler(SaveData)


@adapter(IFormulatorFieldsContext, zs.interfaces.IField)
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
    validators = property(lambda x: _get_(x, 'validators'),
                          lambda x, value: _set_(x, value, 'validators'))


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
            if value:
                data = schema.queryTaggedValue(i, {})
                data[name] = value
                schema.setTaggedValue(i, data)
        # serverSide
        value = fieldNode.get(ns('serverSide', self.namespace))
        if value:
            data = schema.queryTaggedValue('serverSide', {})
            data[name] = value == 'True' or value == 'true'
            schema.setTaggedValue('serverSide', data)
        # validators
        value = fieldNode.get(ns('validators', self.namespace))
        if value:
            data = schema.queryTaggedValue('validators', {})
            data[name] = value.split("|")
            schema.setTaggedValue('validators', data)

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
        # validators
        value = schema.queryTaggedValue('validators', {}).get(name, None)
        if value:
            fieldNode.set(ns('validators', self.namespace), "|".join(value))


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
