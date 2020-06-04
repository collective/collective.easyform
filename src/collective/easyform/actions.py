# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from BTrees.IOBTree import IOBTree
from BTrees.LOBTree import LOBTree as SavedDataBTree
from collective.easyform import easyformMessageFactory as _
from collective.easyform.api import dollar_replacer
from collective.easyform.api import filter_fields
from collective.easyform.api import filter_widgets
from collective.easyform.api import format_addresses
from collective.easyform.api import get_context
from collective.easyform.api import get_expression
from collective.easyform.api import get_schema
from collective.easyform.api import is_file_data
from collective.easyform.api import lnbr
from collective.easyform.api import OrderedDict
from collective.easyform.interfaces import IAction
from collective.easyform.interfaces import IActionFactory
from collective.easyform.interfaces import ICustomScript
from collective.easyform.interfaces import IExtraData
from collective.easyform.interfaces import IMailer
from collective.easyform.interfaces import ISaveData
from copy import deepcopy
from csv import writer as csvwriter
from datetime import date
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from decimal import Decimal
from email import encoders
from email.header import Header
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from json import dumps
from logging import getLogger
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.autoform.view import WidgetsView
from plone.supermodel.exportimport import BaseHandler
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PythonScripts.PythonScript import PythonScript
from six import BytesIO
from six import StringIO
from time import time
from xml.etree import ElementTree as ET
from z3c.form.interfaces import DISPLAY_MODE
from zope.component import queryUtility
from zope.contenttype import guess_content_type
from zope.interface import implementer
from zope.schema import Bool
from zope.schema import getFieldsInOrder
from zope.security.interfaces import IPermission

import six


logger = getLogger("collective.easyform")


@implementer(IActionFactory)
class ActionFactory(object):

    title = u""

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


@implementer(IAction)
class Action(Bool):
    """Base action class.
    """

    def onSuccess(self, fields, request):
        raise NotImplementedError(
            "There is not implemented 'onSuccess' of {0!r}".format(self)
        )


class DummyFormView(WidgetsView):
    """A dummy form to get the widgets rendered for the mailer action.
    """

    mode = DISPLAY_MODE
    ignoreContext = True
    ignoreRequest = False


@implementer(IMailer)
class Mailer(Action):
    __doc__ = IMailer.__doc__

    def __init__(self, **kw):
        for i, f in IMailer.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
        super(Mailer, self).__init__(**kw)

    def get_portal_email_address(self, context):
        """Return the email address defined in the Plone site.
        """
        return api.portal.get_registry_record("plone.email_from_address")

    def secure_header_line(self, line):
        if not line:
            return ""
        nlpos = line.find("\x0a")
        if nlpos >= 0:
            line = line[:nlpos]
        nlpos = line.find("\x0d")
        if nlpos >= 0:
            line = line[:nlpos]
        return line

    def get_mail_body(self, unsorted_data, request, context):
        """Returns the mail-body with footer.
        """
        schema = get_schema(context)

        form = DummyFormView(context, request)
        form.schema = schema
        form.prefix = "form"
        form._update()
        widgets = filter_widgets(self, form.w)
        data = filter_fields(self, schema, unsorted_data)

        bodyfield = self.body_pt

        # pass both the bare_fields (fgFields only) and full fields.
        # bare_fields for compatability with older templates,
        # full fields to enable access to htmlValue
        if isinstance(self.body_pre, six.string_types):
            body_pre = self.body_pre
        else:
            body_pre = self.body_pre.output

        if isinstance(self.body_post, six.string_types):
            body_post = self.body_post
        else:
            body_post = self.body_post.output

        if isinstance(self.body_footer, six.string_types):
            body_footer = self.body_footer
        else:
            body_footer = self.body_footer.output

        extra = {
            "data": data,
            "fields": OrderedDict([(i, j.title) for i, j in getFieldsInOrder(schema)]),
            "widgets": widgets,
            "mailer": self,
            "body_pre": body_pre and lnbr(dollar_replacer(body_pre, data)),
            "body_post": body_post and lnbr(dollar_replacer(body_post, data)),
            "body_footer": body_footer and lnbr(dollar_replacer(body_footer, data)),
        }
        template = ZopePageTemplate(self.__name__)
        template.write(bodyfield)
        template = template.__of__(context)
        return template.pt_render(extra_context=extra)

    def get_owner_info(self, context):
        """Return owner info.
        """
        pms = getToolByName(context, "portal_membership")
        ownerinfo = context.getOwner()
        ownerid = fullname = ownerinfo.getId()
        userdest = pms.getMemberById(ownerid)
        if userdest is not None:
            fullname = userdest.getProperty("fullname", ownerid)
        toemail = ""
        if userdest is not None:
            toemail = userdest.getProperty("email", "")
        if not toemail:
            toemail = self.get_portal_email_address(context)
        if not toemail:
            raise ValueError(
                u"Unable to mail form input because no recipient address has "
                u"been specified. Please check the recipient settings of the "
                u"EasyForm Mailer within the current form folder."
            )
        return (fullname, toemail)

    def get_addresses(self, fields, request, context, from_addr=None, to_addr=None):
        """Return addresses.
        """
        # get Reply-To
        reply_addr = None
        if hasattr(self, "replyto_field"):
            reply_addr = fields.get(self.replyto_field, None)

        # Get From address
        portal_addr = self.get_portal_email_address(context)
        from_addr = from_addr or portal_addr

        if hasattr(self, "senderOverride") and self.senderOverride:
            _from = get_expression(context, self.senderOverride, fields=fields)
            if _from:
                from_addr = _from

        # Get To address and full name
        recip_email = None
        if hasattr(self, "to_field") and self.to_field:
            recip_email = fields.get(self.to_field, None)
        if not recip_email:
            if self.recipient_email != "":
                recip_email = self.recipient_email

        if hasattr(self, "recipientOverride") and self.recipientOverride:
            _recip = get_expression(context, self.recipientOverride, fields=fields)
            if _recip:
                recip_email = _recip

        to = None
        if to_addr:
            to = format_addresses(to_addr)
        elif recip_email:
            to = format_addresses(recip_email, self.recipient_name)
        else:
            # Use owner adress or fall back to portal email_from_address.
            to = formataddr(self.get_owner_info(context))

        assert to
        return (to, from_addr, reply_addr)

    def get_subject(self, fields, request, context):
        """Return subject.
        """
        # get subject header
        nosubject = u"(no subject)"  # TODO: translate
        subject = None
        if hasattr(self, "subjectOverride") and self.subjectOverride:
            # subject has a TALES override
            subject = get_expression(
                context, self.subjectOverride, fields=fields
            ).strip()

        if not subject:
            subject = getattr(self, "msg_subject", nosubject)
            subjectField = fields.get(self.subject_field, None)
            if subjectField is not None:
                subject = subjectField
            else:
                # we only do subject expansion if there's no field chosen
                subject = dollar_replacer(subject, fields)

        if isinstance(subject, six.string_types):
            subject = safe_unicode(subject)
        elif subject and isinstance(subject, (set, tuple, list)):
            subject = ", ".join([safe_unicode(s) for s in subject])
        else:
            subject = nosubject

        # transform subject into mail header encoded string
        email_charset = "utf-8"
        msgSubject = self.secure_header_line(subject).encode(email_charset, "replace")
        return Header(msgSubject, email_charset)

    def get_header_info(
        self, fields, request, context, from_addr=None, to_addr=None, subject=None
    ):
        """Return header info.

        header info is a dictionary

        Keyword arguments:
        request -- (optional) alternate request object to use
        """
        (to, from_addr, reply) = self.get_addresses(fields, request, context)

        headerinfo = OrderedDict()
        headerinfo["To"] = self.secure_header_line(to)
        headerinfo["From"] = self.secure_header_line(from_addr)
        if reply:
            headerinfo["Reply-To"] = self.secure_header_line(reply)
        headerinfo["Subject"] = self.get_subject(fields, request, context)

        # CC
        if isinstance(self.cc_recipients, six.string_types):
            cc_recips = self.cc_recipients
        else:
            cc_recips = [_f for _f in self.cc_recipients if _f]
        if hasattr(self, "ccOverride") and self.ccOverride:
            _cc = get_expression(context, self.ccOverride, fields=fields)
            if _cc:
                cc_recips = _cc

        if cc_recips:
            headerinfo["Cc"] = format_addresses(cc_recips)

        # BCC
        if isinstance(self.bcc_recipients, six.string_types):
            bcc_recips = self.bcc_recipients
        else:
            bcc_recips = [_f for _f in self.bcc_recipients if _f]
        if hasattr(self, "bccOverride") and self.bccOverride:
            _bcc = get_expression(context, self.bccOverride, fields=fields)
            if _bcc:
                bcc_recips = _bcc

        if bcc_recips:
            headerinfo["Bcc"] = format_addresses(bcc_recips)

        for key in getattr(self, "xinfo_headers", []):
            headerinfo["X-{0}".format(key)] = self.secure_header_line(
                request.get(key, "MISSING")
            )

        return headerinfo

    def serialize(self, field):
        """Serializa field to save to XML.
        """
        if field is None:
            return ""
        if isinstance(field, (set, list, tuple)):
            list_value = list([self.serialize(f) for f in field])
            return dumps(list_value)
        if isinstance(field, dict):
            dict_value = {str(key): self.serialize(val) for key, val in field.items()}
            return dumps(dict_value)
        if isinstance(field, RichTextValue):
            return field.raw
        if isinstance(field, datetime):
            return field.strftime("%Y/%m/%d, %H:%M:%S")
        if isinstance(field, date):
            return field.strftime("%Y/%m/%d")
        if isinstance(field, timedelta):
            return str(field)
        if isinstance(field, (int, float, Decimal, bool)):
            return str(field)
        if isinstance(field, six.string_types):
            return safe_unicode(field)
        return safe_unicode(repr(field))

    def get_attachments(self, fields, request):
        """Return all attachments uploaded in form.
        """

        attachments = []

        # if requested, generate CSV attachment of form values
        sendCSV = getattr(self, "sendCSV", None)
        if sendCSV:
            csvdata = ()
        sendXML = getattr(self, "sendXML", None)
        if sendXML:
            xmlRoot = ET.Element("form")
        showFields = getattr(self, "showFields", []) or []
        for fname in fields:
            field = fields[fname]

            if sendCSV:
                if not is_file_data(field) and (
                    getattr(self, "showAll", True) or fname in showFields
                ):
                    val = self.serialize(field)
                    if six.PY2:
                        val = val.encode("utf-8")
                    csvdata += (val,)

            if sendXML:
                if not is_file_data(field) and (
                    getattr(self, "showAll", True) or fname in showFields
                ):
                    ET.SubElement(xmlRoot, "field", name=fname).text = self.serialize(
                        field
                    )  # noqa

            if is_file_data(field) and (
                getattr(self, "showAll", True) or fname in showFields
            ):
                data = field.data
                filename = field.filename
                mimetype, enc = guess_content_type(filename, data, None)
                attachments.append((filename, mimetype, enc, data))

        if sendCSV:
            output = StringIO()
            writer = csvwriter(output)
            writer.writerow(csvdata)
            csv = output.getvalue()
            if six.PY3:
                csv = csv.encode("utf-8")
            now = DateTime().ISO().replace(" ", "-").replace(":", "")
            filename = "formdata_{0}.csv".format(now)
            # Set MIME type of attachment to 'application' so that it will be encoded with base64
            attachments.append((filename, "application/csv", "utf-8", csv))

        if sendXML:
            # use ET.write to get a proper XML Header line
            output = BytesIO()
            doc = ET.ElementTree(xmlRoot)
            doc.write(output, encoding="utf-8", xml_declaration=True)
            xmlstr = output.getvalue()
            now = DateTime().ISO().replace(" ", "-").replace(":", "")
            filename = "formdata_{0}.xml".format(now)
            # Set MIME type of attachment to 'application' so that it will be encoded with base64
            attachments.append((filename, "application/xml", "utf-8", xmlstr))

        return attachments

    def get_mail_text(self, fields, request, context):
        """Get header and body of e-mail as text (string)
        """
        headerinfo = self.get_header_info(fields, request, context)
        body = self.get_mail_body(fields, request, context)
        if six.PY2 and isinstance(body, six.text_type):
            body = body.encode("utf-8")
        email_charset = "utf-8"
        # always use text/plain for encrypted bodies
        subtype = (
            getattr(self, "gpg_keyid", False) and "plain" or self.body_type or "html"
        )
        mime_text = MIMEText(
            safe_unicode(body).encode(email_charset, "replace"),
            _subtype=subtype,
            _charset=email_charset,
        )

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
            key, value = a.split(":", 1)
            outer.add_header(key, value.strip())

        for attachment in attachments:
            filename = attachment[0]
            ctype = attachment[1]
            # encoding = attachment[2]
            content = attachment[3]
            if ctype is None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            if maintype == "text":
                if not six.PY2 and isinstance(content, six.binary_type):
                    content = content.decode("utf-8")
                msg = MIMEText(content, _subtype=subtype)
            elif maintype == "image":
                msg = MIMEImage(content, _subtype=subtype)
            elif maintype == "audio":
                msg = MIMEAudio(content, _subtype=subtype)
            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(content)
                # Encode the payload using Base64
                encoders.encode_base64(msg)

            # Set the filename parameter
            if six.PY2 and isinstance(filename, six.text_type):
                filename = filename.encode("utf-8")
            msg.add_header(
                "Content-Disposition", "attachment", filename=("utf-8", "", filename)
            )
            outer.attach(msg)

        return outer.as_string()

    def onSuccess(self, fields, request):
        """e-mails data.
        """
        context = get_context(self)
        mailtext = self.get_mail_text(fields, request, context)
        host = api.portal.get_tool(name="MailHost")
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

        # Skip check roles
        script._validateProxy = lambda i=None: None

        # Force proxy role
        if role != u"none":
            script.manage_proxy((role,))

        if six.PY2 and isinstance(body, six.text_type):
            body = body.encode("utf-8")
        params = "fields, easyform, request"
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
            logger.warning(
                "Python script "
                + self.__name__
                + " has warning:"
                + str(script.warnings)
            )

        if len(script.errors) > 0:
            logger.error(
                "Python script " + self.__name__ + " has errors: " + str(script.errors)
            )
            raise ValueError(
                "Python script {0} has errors: {1}".format(
                    self.__name__, str(script.errors)
                )
            )

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


@implementer(ISaveData)
class SaveData(Action):
    __doc__ = ISaveData.__doc__

    def __init__(self, **kw):
        for i, f in ISaveData.namesAndDescriptions():
            setattr(self, i, kw.pop(i, f.default))
        super(SaveData, self).__init__(**kw)

    @property
    def _storage(self):
        context = get_context(self)
        if not hasattr(context, "_inputStorage"):
            context._inputStorage = {}
        if self.__name__ not in context._inputStorage:
            context._inputStorage[self.__name__] = SavedDataBTree()
        return context._inputStorage[self.__name__]

    def clearSavedFormInput(self):
        # convenience method to clear input buffer
        self._storage.clear()

    def getSavedFormInput(self):
        """Returns saved input as an iterable;
        each row is a sequence of fields.
        """

        return list(self._storage.values())

    def getSavedFormInputItems(self):
        """Returns saved input as an iterable;
        each row is an (id, sequence of fields) tuple
        """
        return list(self._storage.items())

    def getSavedFormInputForEdit(self, header=False, delimiter=","):
        """Returns saved as CSV text"""
        sbuf = StringIO()
        writer = csvwriter(sbuf, delimiter=delimiter)
        names = self.getColumnNames()
        titles = self.getColumnTitles()

        if header:
            encoded_titles = []
            for t in titles:
                if six.PY2 and isinstance(t, six.text_type):
                    t = t.encode("utf-8")
                encoded_titles.append(t)
            writer.writerow(encoded_titles)
        for row in self.getSavedFormInput():

            def get_data(row, i):
                data = row.get(i, "")
                if is_file_data(data):
                    data = data.filename
                if six.PY2 and isinstance(data, six.text_type):
                    return data.encode("utf-8")
                return data

            row_data = [get_data(row, i) for i in names]
            writer.writerow(row_data)
        res = sbuf.getvalue()
        sbuf.close()
        return res

    def getColumnNames(self):
        # """Returns a list of column names"""
        context = get_context(self)
        showFields = getattr(self, "showFields", [])
        if showFields is None:
            showFields = []
        names = [
            name
            for name, field in getFieldsInOrder(get_schema(context))
            if not showFields or name in showFields
        ]
        if self.ExtraData:
            for f in self.ExtraData:
                names.append(f)
        return names

    def getColumnTitles(self):
        # """Returns a list of column titles"""
        context = get_context(self)
        showFields = getattr(self, "showFields", [])
        if showFields is None:
            showFields = []

        names = [
            field.title
            for name, field in getFieldsInOrder(get_schema(context))
            if not showFields or name in showFields
        ]
        if self.ExtraData:
            for f in self.ExtraData:
                names.append(IExtraData[f].title)
        return names

    def download_csv(self, response):
        # """Download the saved data as csv
        # """
        response.setHeader(
            "Content-Disposition",
            'attachment; filename="{0}.csv"'.format(self.__name__),
        )
        response.setHeader("Content-Type", "text/comma-separated-values")
        value = self.getSavedFormInputForEdit(
            getattr(self, "UseColumnNames", False), delimiter=","
        )
        if isinstance(value, six.text_type):
            value = value.encode("utf-8")
        response.write(value)

    def download_tsv(self, response):
        # """Download the saved data as tsv
        # """
        response.setHeader(
            "Content-Disposition",
            'attachment; filename="{0}.tsv"'.format(self.__name__),
        )
        response.setHeader("Content-Type", "text/tab-separated-values")
        value = self.getSavedFormInputForEdit(
            getattr(self, "UseColumnNames", False), delimiter="\t"
        )
        if isinstance(value, six.text_type):
            value = value.encode("utf-8")
        response.write(value)

    def download(self, response):
        # """Download the saved data
        # """
        format = getattr(self, "DownloadFormat", "tsv")
        if format == "tsv":
            return self.download_tsv(response)
        else:
            assert format == "csv", "Unknown download format"
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
        value["id"] = id
        storage[id] = value

    def onSuccess(self, fields, request):
        """Saves data.
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
        showFields = getattr(self, "showFields", []) or self.getColumnNames()
        for f in fields:
            if f not in showFields:
                continue
            data[f] = fields[f]

        if self.ExtraData:
            for f in self.ExtraData:
                if f == "dt":
                    data[f] = str(DateTime())
                else:
                    data[f] = getattr(request, f, "")

        self.addDataRow(data)


MailerAction = ActionFactory(
    Mailer,
    _(u"label_mailer_action", default=u"Mailer"),
    "collective.easyform.AddMailers",
)
CustomScriptAction = ActionFactory(
    CustomScript,
    _(u"label_customscript_action", default=u"Custom Script"),
    "collective.easyform.AddCustomScripts",
)
SaveDataAction = ActionFactory(
    SaveData,
    _(u"label_savedata_action", default=u"Save Data"),
    "collective.easyform.AddDataSavers",
)

MailerHandler = BaseHandler(Mailer)
CustomScriptHandler = BaseHandler(CustomScript)
SaveDataHandler = BaseHandler(SaveData)
