# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from App.class_init import InitializeClass
from BTrees.IOBTree import IOBTree
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PythonScripts.PythonScript import PythonScript
from StringIO import StringIO
from collections import OrderedDict as BaseDict
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import DollarVarReplacer
from collective.easyform.api import filter_fields
from collective.easyform.api import format_addresses
from collective.easyform.api import get_context
from collective.easyform.api import get_expression
from collective.easyform.api import get_fields
from collective.easyform.interfaces import IAction
from collective.easyform.interfaces import IActionFactory
from collective.easyform.interfaces import ICustomScript
from collective.easyform.interfaces import IExtraData
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.interfaces import IMailer
from collective.easyform.interfaces import ISaveData
from copy import deepcopy
from csv import writer as csvwriter
from email import Encoders
from email.Header import Header
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.utils import formataddr
from logging import getLogger
from plone.namedfile.interfaces import INamedBlobFile
from plone.namedfile.interfaces import INamedFile
from plone.supermodel.exportimport import BaseHandler
from time import time
from types import StringTypes
from zope.component import queryUtility
from zope.contenttype import guess_content_type
from zope.interface import implements
from zope.schema import Bool
from zope.schema import getFieldsInOrder
from zope.security.interfaces import IPermission
try:
    from BTrees.LOBTree import LOBTree
    SavedDataBTree = LOBTree
except ImportError:
    SavedDataBTree = IOBTree
logger = getLogger('collective.easyform')


class OrderedDict(BaseDict):
    """
    A wrapper around dictionary objects that provides an ordering for
    keys() and items().
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def reverse(self):
        items = list(self.items())
        items.reverse()
        return items


InitializeClass(OrderedDict)


class ActionFactory(object):
    implements(IActionFactory)

    title = u''

    def __init__(self, fieldcls, title, permission, *args, **kw):
        self.fieldcls = fieldcls
        self.title = title
        self.permission = permission
        self.args = args
        self.kw = kw

    def available(self, context):
        """ field is addable in the current context """
        securityManager = getSecurityManager()
        permission = queryUtility(IPermission, name=self.permission)
        if permission is None:
            return True
        return bool(securityManager.checkPermission(permission.title, context))

    def editable(self, field):
        """ test whether a given instance of a field is editable """
        return True

    def __call__(self, *args, **kw):
        kwargs = deepcopy(self.kw)
        kwargs.update(**kw)
        return self.fieldcls(*(self.args + args), **kwargs)


class Action(Bool):

    """ Base action class """
    implements(IAction)

    def onSuccess(self, fields, request):
        raise NotImplementedError(
            "There is not implemented 'onSuccess' of {0!r}".format(self))

    def _is_file_data(self, value):
        ifaces = (INamedFile, INamedBlobFile)
        for i in ifaces:
            if i.providedBy(value):
                return True
        return False


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

    def get_mail_body(self, fields, request, context):
        """Returns the mail-body with footer.
        """

        schema = get_fields(context)
        data = filter_fields(self, schema, fields)
        bodyfield = self.body_pt

        # pass both the data (fgFields only) and full fields.
        # data for compatability with older templates,
        # full fields to enable access to htmlValue
        # The default mailer iterates over the data,
        # so the order of the data is kept.
        replacer = DollarVarReplacer(fields).sub
        extra = {
            'data': data,
            'fields': OrderedDict([
                (i, j.title)
                for i, j in getFieldsInOrder(schema)
            ]),
            'mailer': self,
            'body_pre': self.body_pre and replacer(self.body_pre),
            'body_post': self.body_post and replacer(self.body_post),
            'body_footer': self.body_footer and replacer(self.body_footer),
        }
        template = ZopePageTemplate(self.__name__)
        template.write(bodyfield)
        template = template.__of__(context)
        body = template.pt_render(extra_context=extra)

        return body

    def get_owner_info(self, context):
        """Return owner info
        """
        pms = getToolByName(context, 'portal_membership')
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
            portal = getToolByName(context, 'portal_url').getPortalObject()
            toemail = portal.getProperty('email_from_address')
        assert toemail, """
                Unable to mail form input because no recipient address has been specified.
                Please check the recipient settings of the EasyForm "Mailer" within the
                current form folder.
            """
        return (fullname, toemail)

    def get_addresses(self, fields, request, context, from_addr=None, to_addr=None):
        """Return addresses
        """
        pprops = getToolByName(context, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        portal = getToolByName(context, 'portal_url').getPortalObject()

        # get Reply-To
        reply_addr = None
        if hasattr(self, 'replyto_field'):
            reply_addr = fields.get(self.replyto_field, None)

        # Get From address
        from_addr = (
            from_addr or
            site_props.getProperty('email_from_address') or
            portal.getProperty('email_from_address')
        )

        if hasattr(self, 'senderOverride') and self.senderOverride:
            _from = get_expression(context, self.senderOverride, fields=fields)
            if _from:
                from_addr = _from

        # Get To address and full name
        recip_email = None
        if hasattr(self, 'to_field') and self.to_field:
            recip_email = fields.get(self.to_field, None)
        if not recip_email:
            recip_email = self.recipient_email

        if hasattr(self, 'recipientOverride') and self.recipientOverride:
            _recip = get_expression(
                context,
                self.recipientOverride,
                fields=fields
            )
            if _recip:
                recip_email = _recip

        to = None
        if to_addr:
            to = format_addresses(to_addr)
        elif recip_email:
            to = format_addresses(
                recip_email,
                self.recipient_name
            )
        else:
            # Use owner adress or fall back to portal email_from_address.
            to = formataddr(self.get_owner_info(context))

        assert(to)
        return (to, from_addr, reply_addr)

    def get_subject(self, fields, request, context):
        """Return subject
        """
        # get subject header
        nosubject = '(no subject)'
        subject = None
        if hasattr(self, 'subjectOverride') and self.subjectOverride:
            # subject has a TALES override
            subject = get_expression(
                context,
                self.subjectOverride,
                fields=fields
            ).strip()

        if not subject:
            subject = getattr(self, 'msg_subject', nosubject)
            subjectField = fields.get(self.subject_field, None)
            if subjectField is not None:
                subject = subjectField
            else:
                # we only do subject expansion if there's no field chosen
                subject = DollarVarReplacer(fields).sub(subject)

        return subject

    def get_header_info(self, fields, request, context,
                        from_addr=None, to_addr=None,
                        subject=None):
        """Return header info

        header info is a dictionary

        Keyword arguments:
        request -- (optional) alternate request object to use
        """
        portal = getToolByName(context, 'portal_url').getPortalObject()
        utils = getToolByName(context, 'plone_utils')
        (to, from_addr, reply) = self.get_addresses(fields, request, context)
        subject = self.get_subject(fields, request, context)

        headerinfo = OrderedDict()

        headerinfo['To'] = self.secure_header_line(to)
        headerinfo['From'] = self.secure_header_line(from_addr)
        if reply:
            headerinfo['Reply-To'] = self.secure_header_line(reply)

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
        if hasattr(self, 'ccOverride') and self.ccOverride:
            _cc = get_expression(context, self.ccOverride, fields=fields)
            if _cc:
                cc_recips = _cc

        if cc_recips:
            headerinfo['Cc'] = format_addresses(cc_recips)

        # BCC
        bcc_recips = filter(None, self.bcc_recipients)
        if hasattr(self, 'bccOverride') and self.bccOverride:
            _bcc = get_expression(context, self.bccOverride, fields=fields)
            if _bcc:
                bcc_recips = _bcc

        if bcc_recips:
            headerinfo['Bcc'] = format_addresses(bcc_recips)

        for key in getattr(self, 'xinfo_headers', []):
            headerinfo['X-{0}'.format(key)] = self.secure_header_line(
                request.get(key, 'MISSING'))

        return headerinfo

    def get_attachments(self, fields, request):
        """Return all attachments uploaded in form.
        """

        attachments = []

        for fname in fields:
            field = fields[fname]
            showFields = getattr(self, 'showFields', []) or []

            if self._is_file_data(field) and (
                    getattr(self, 'showAll', True) or fname in showFields):
                data = field.data
                filename = field.filename
                mimetype, enc = guess_content_type(filename, data, None)
                attachments.append((filename, mimetype, enc, data))
        return attachments

    def get_mail_text(self, fields, request, context):
        """Get header and body of e-mail as text (string)
        """

        headerinfo = self.get_header_info(fields, request, context)
        body = self.get_mail_body(fields, request, context)

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
        additional_headers = self.additional_headers or []
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
        mailtext = self.get_mail_text(fields, request, context)
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
        if role != u'none':
            script.manage_proxy((role,))

        body = body.encode('utf-8')
        params = 'fields, easyform, request'
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
            logger.warn('Python script ' + self.__name__
                        + ' has warning:' + str(script.warnings))

        if len(script.errors) > 0:
            logger.error('Python script ' + self.__name__
                         + ' has errors: ' + str(script.errors))
            raise ValueError(
                'Python script ' + self.__name__ + ' has errors: ' + str(script.errors))

    def executeCustomScript(self, result, form, req):
        # Execute in-place script

        # @param result Extracted fields from request.form
        # @param form EasyForm object

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
        if self.__name__ not in context._inputStorage:
            context._inputStorage[self.__name__] = SavedDataBTree()
        return context._inputStorage[self.__name__]

    def clearSavedFormInput(self):
        # convenience method to clear input buffer
        self._storage.clear()

    def getSavedFormInput(self):
        """ returns saved input as an iterable;
            each row is a sequence of fields.
        """

        return self._storage.values()

    def getSavedFormInputItems(self):
        """ returns saved input as an iterable;
            each row is an (id, sequence of fields) tuple
        """
        return self._storage.items()

    def getSavedFormInputForEdit(self, header=False, delimiter=','):
        """ returns saved as CSV text """
        sbuf = StringIO()
        writer = csvwriter(sbuf, delimiter=delimiter)
        names = self.getColumnNames()
        titles = self.getColumnTitles()

        if header:
            encoded_titles = []
            for t in titles:
                if isinstance(t, unicode):
                    t = t.encode('utf-8')
                encoded_titles.append(t)
            writer.writerow(encoded_titles)
        for row in self.getSavedFormInput():
            def get_data(row, i):
                data = row.get(i, '')
                if self._is_file_data(data):
                    return data.filename
                if isinstance(data, unicode):
                    return data.encode('utf-8')
                return data
            writer.writerow([get_data(row, i) for i in names])
        res = sbuf.getvalue()
        sbuf.close()
        return res

    def getColumnNames(self):
        # """Returns a list of column names"""
        context = get_context(self)
        showFields = getattr(self, 'showFields', [])
        if showFields is None:
            showFields = []
        names = [
            name
            for name, field in getFieldsInOrder(get_fields(context))
            if not showFields or name in showFields
        ]
        if self.ExtraData:
            for f in self.ExtraData:
                names.append(f)
        return names

    def getColumnTitles(self):
        # """Returns a list of column titles"""
        context = get_context(self)
        showFields = getattr(self, 'showFields', [])
        if showFields is None:
            showFields = []

        names = [
            field.title
            for name, field in getFieldsInOrder(get_fields(context))
            if not showFields or name in showFields
        ]
        if self.ExtraData:
            for f in self.ExtraData:
                names.append(IExtraData[f].title)
        return names

    def download_csv(self, response):
        # """Download the saved data as csv
        # """
        response.setHeader('Content-Disposition',
                           'attachment; filename="{0}.csv"'.format(self.__name__))
        response.setHeader('Content-Type', 'text/comma-separated-values')
        response.write(self.getSavedFormInputForEdit(
            getattr(self, 'UseColumnNames', False), delimiter=','))

    def download_tsv(self, response):
        # """Download the saved data as tsv
        # """
        response.setHeader('Content-Disposition',
                           'attachment; filename="{0}.tsv"'.format(self.__name__))
        response.setHeader('Content-Type', 'text/tab-separated-values')
        response.write(self.getSavedFormInputForEdit(
            getattr(self, 'UseColumnNames', False), delimiter='\t'))

    def download(self, response):
        # """Download the saved data
        # """
        format = getattr(self, 'DownloadFormat', 'tsv')
        if format == 'tsv':
            return self.download_tsv(response)
        else:
            assert format == 'csv', 'Unknown download format'
            return self.download_csv(response)

    def itemsSaved(self):
        return len(self._storage)

    def delDataRow(self, key):
        del self._storage[key]

    def setDataRow(self, key, value):
        # sdata = self.storage[id]
        # sdata.update(data)
        # self.storage[id] = sdata
        self._storage[key] = value

    def addDataRow(self, value):
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
        # parent = self.aq_parent
        # if safe_hasattr(parent, 'isTranslation') and \
        # parent.isTranslation() and not parent.isCanonical():
        # look in the canonical version to see if there is
        # a matching (by id) save-data adapter.
        # If so, call its onSuccess method
        # cf = parent.getCanonical()
        # target = cf.get(self.getId())
        # if target is not None and target.meta_type == 'FormSaveDataAdapter':
        # target.onSuccess(fields, request, loopstop=True)
        # return
        data = {}
        showFields = getattr(self, 'showFields', []) or self.getColumnNames()
        for f in fields:
            if f not in showFields:
                continue
            data[f] = fields[f]

        if self.ExtraData:
            for f in self.ExtraData:
                if f == 'dt':
                    data[f] = str(DateTime())
                else:
                    data[f] = getattr(request, f, '')

        self.addDataRow(data)


MailerAction = ActionFactory(
    Mailer, _(u'label_mailer_action', default=u'Mailer'), 'collective.easyform.AddMailers')
CustomScriptAction = ActionFactory(
    CustomScript, _(u'label_customscript_action', default=u'Custom Script'), 'collective.easyform.AddCustomScripts')
SaveDataAction = ActionFactory(
    SaveData, _(u'label_savedata_action', default=u'Save Data'), 'collective.easyform.AddDataSavers')

MailerHandler = BaseHandler(Mailer)
CustomScriptHandler = BaseHandler(CustomScript)
SaveDataHandler = BaseHandler(SaveData)
