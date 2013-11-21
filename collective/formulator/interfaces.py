from zope.interface import Invalid, Interface, invariant
from zope import schema as zs
from zope.schema.interfaces import IField
from z3c.form import interfaces
from zope.schema.vocabulary import SimpleVocabulary
from plone.directives import form
from plone.schemaeditor.interfaces import ID_RE, ISchemaContext, IFieldContext
from collective.formulator import formulatorMessageFactory as _
from plone.schemaeditor import SchemaEditorMessageFactory as __


def isValidFieldName(value):
    if not ID_RE.match(value):
        raise Invalid(__(u'Please use only letters, numbers and '
                         u'the following characters: _.'))
    return True


class INewAction(Interface):

    title = zs.TextLine(
        title=__(u'Title'),
        required=True
    )

    __name__ = zs.ASCIILine(
        title=__(u'Short Name'),
        description=__(u'Used for programmatic access to the field.'),
        required=True,
        constraint=isValidFieldName,
    )

    description = zs.Text(
        title=__(u'Help Text'),
        description=__(u'Shows up in the form as help text for the field.'),
        required=False
    )

    factory = zs.Choice(
        title=_(u"Action type"),
        vocabulary="FormulatorActions",
        required=True,
    )

    @invariant
    def checkTitleAndDescriptionTypes(data):
        if data.__name__ is not None and data.factory is not None:
            if data.__name__ == 'title' and data.factory.fieldcls is not zs.TextLine:
                raise Invalid(
                    __(u"The 'title' field must be a Text line (string) field."))
            if data.__name__ == 'description' and data.factory.fieldcls is not zs.Text:
                raise Invalid(
                    __(u"The 'description' field must be a Text field."))


class IActionFactory(IField):

    """ A component that instantiates a action when called.
    """
    title = zs.TextLine(title=u'Title')


class ICollectiveFormulatorLayer(Interface):

    """ A layer specific to this product.
        Is registered using browserlayer.xml
    """

MODEL_DEFAULT = u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
"""


class IFormulator(form.Schema):

    """Forms for Plone"""

    # -*- schema definition goes here -*-
    model = zs.Text(
        title=u"Model",
        default=MODEL_DEFAULT,
    )

    actions_model = zs.Text(
        title=u"Actions Model",
        default=MODEL_DEFAULT,
    )


class IFormulatorView(Interface):

    """
    Formulator view interface
    """


class IFormulatorSchemaContext(ISchemaContext):

    """
    Formulator schema view interface
    """


class IFormulatorActionsContext(ISchemaContext):

    """
    Formulator actions view interface
    """


class IActionContext(IFieldContext):

    """
    Formulator action view interface
    """


class IActionEditForm(interfaces.IEditForm):

    """ Marker interface for action edit forms
    """


class IAction(zs.interfaces.IField):
    required = zs.Bool(
        title=_("Enabled"),
        description=_("Tells whether a action is enabled."),
        default=True)
    # TODO:
    # TALESString('execCondition',
    # schemata='overrides',
    # validators=('talesvalidator',),
    # write_permission=EDIT_TALES_PERMISSION,
    # read_permission=ModifyPortalContent,
    execCondition = zs.TextLine(
        title=_(u'label_execcondition_text', default=u"Execution Condition"),
        description=(_(u'help_execcondition_text', default=u""
                       u"A TALES expression that will be evaluated to determine whether"
                       u"or not to execute this action. Leave empty if unneeded, and "
                       u"the action will be executed. Your expression should evaluate "
                       u"as a boolean; return True if you wish the action to execute. "
                       u"PLEASE NOTE: errors in the evaluation of this expression will "
                       u"cause an error on form display.")
                     ),
        default=u"",
        required=False,
    )


class IMailer(form.Schema, IAction):

    """A form action adapter that will e-mail form input."""
    form.fieldset(u"overrides", label="Overrides", fields=['execCondition'])
    form.omitted('order', 'default', 'missing_value', 'readonly')
    # StringField('recipient_name',
        # searchable=0,
        # required=0,
        # default_method='getDefaultRecipientName',
        # write_permission=EDIT_ADDRESSING_PERMISSION,
        # read_permission=ModifyPortalContent,
        # widget=StringWidget(
            # label=_(u'label_formmailer_recipient_fullname',
                      # default=u"Recipient's full name"),
            # description=_(u'help_formmailer_recipient_fullname', default=u"""
                # The full name of the recipient of the mailed form.
                #"""),
            #),
        #),
    # StringField('recipient_email',
        # searchable=0,
        # required=0,
        # default_method='getDefaultRecipient',
        # write_permission=EDIT_ADDRESSING_PERMISSION,
        # read_permission=ModifyPortalContent,
        # validators=('isEmail',),
        # widget=StringWidget(
            # label=_(u'label_formmailer_recipient_email',
                      # default=u"Recipient's e-mail address"),
            # description=_(u'help_formmailer_recipient_email',
                            # default=u'The recipients e-mail address.'),
            #),
        #),
    # StringField('to_field',
        # schemata='addressing',
        # searchable=0,
        # required=0,
        # default='#NONE#',
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # read_permission=ModifyPortalContent,
        # vocabulary='fieldsDisplayList',
        # widget=SelectionWidget(
            #label=_(u'label_formmailer_to_extract', default=u'Extract Recipient From'),
            # description=_(u'help_formmailer_to_extract',
                # default=u"""
                # Choose a form field from which you wish to extract
                # input for the To header. If you choose anything other
                # than "None", this will override the "Recipient's e-mail address"
                # setting above. Be very cautious about allowing unguarded user
                # input for this purpose.
                #"""),
            #),
        #),
    # LinesField('cc_recipients',
        # searchable=0,
        # required=0,
        # default_method='getDefaultCC',
        # schemata='addressing',
        # write_permission=EDIT_ADDRESSING_PERMISSION,
        # read_permission=ModifyPortalContent,
        # widget=LinesWidget(
            # label=_(u'label_formmailer_cc_recipients',
                      # default=u'CC Recipients'),
            # description=_(u'help_formmailer_cc_recipients',
                    # default=u'E-mail addresses which receive a carbon copy.'),
            #),
        #),
    # LinesField('bcc_recipients',
        # schemata='addressing',
        # searchable=0,
        # required=0,
        # default_method='getDefaultBCC',
        # write_permission=EDIT_ADDRESSING_PERMISSION,
        # read_permission=ModifyPortalContent,
        # widget=LinesWidget(
            # label=_(u'label_formmailer_bcc_recipients',
                      # default=u'BCC Recipients'),
            # description=_(u'help_formmailer_bcc_recipients',
                # default=u'E-mail addresses which receive a blind carbon copy.'),
            #),
        #),
    # StringField('replyto_field',
        # schemata='addressing',
        # searchable=0,
        # required=0,
        # vocabulary='fieldsDisplayList',
        # read_permission=ModifyPortalContent,
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # widget=SelectionWidget(
            # label=_(u'label_formmailer_replyto_extract',
                      # default=u'Extract Reply-To From'),
            # description=_(u'help_formmailer_replyto_extract',
                # default=u"""
                # Choose a form field from which you wish to extract
                # input for the Reply-To header. NOTE: You should
                # activate e-mail address verification for the designated
                # field.
                #"""),
            #),
        #),
    # StringField('smtp_envelope_mail_from',
        # schemata='addressing',
        # searchable=0,
        # required=0,
        # read_permission=ModifyPortalContent,
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # widget=StringWidget(
            # label = _(u'label_smtp_envelope_mail_from_address',
                      # default=u'SMTP Envelope MAIL FROM address'),
            # description = _(u'help_smtp_envelope_mail_from_address', default=\
                # u"""
                #"""),
            #),
        #),
    # StringField('msg_subject',
        # schemata='message',
        # searchable=0,
        # required=0,
        #default='Form Submission',
        # read_permission=ModifyPortalContent,
        # widget=StringWidget(
            # description=_(u'help_formmailer_subject',
                # default=u"""
                # Subject line of message. This is used if you
                # do not specify a subject field or if the field
                # is empty.
                #"""),
            #label=_(u'label_formmailer_subject', default=u'Subject'),
            #),
        #),
    # StringField('subject_field',
        # schemata='message',
        # searchable=0,
        # required=0,
        # vocabulary='fieldsDisplayList',
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # read_permission=ModifyPortalContent,
        # widget=SelectionWidget(
            # label=_(u'label_formmailer_subject_extract',
                      # default=u'Extract Subject From'),
            # description=_(u'help_formmailer_subject_extract',
            # default=u"""
                # Choose a form field from which you wish to extract
                # input for the mail subject line.
                #"""),
            #),
        #),
    # TextField('body_pre',
        # searchable=0,
        # required=0,
        # schemata='message',
        # accessor='getBody_pre',
        # read_permission=ModifyPortalContent,
        # default_content_type='text/plain',
        # allowable_content_types=('text/plain',),
        # widget=TextAreaWidget(description=_(u'help_formmailer_body_pre',
                      # default=u'Text prepended to fields listed in mail-body'),
          #label=_(u'label_formmailer_body_pre', default=u'Body (prepended)'),
            #),
        #),
    # TextField('body_post',
        # searchable=0,
        # required=0,
        # schemata='message',
        # read_permission=ModifyPortalContent,
        # default_content_type='text/plain',
        # allowable_content_types=('text/plain',),
        # widget=TextAreaWidget(description=_(u'help_formmailer_body_post',
                      # default=u'Text appended to fields listed in mail-body'),
          #label=_(u'label_formmailer_body_post', default=u'Body (appended)'),
            #),
        #),

    # TextField('body_footer',
        # searchable=0,
        # required=0,
        # schemata='message',
        # read_permission=ModifyPortalContent,
        # default_content_type='text/plain',
        # allowable_content_types=('text/plain',),
        # widget=TextAreaWidget(description=_(u'help_formmailer_body_footer',
                          #default=u'Text used as the footer at '
                          # u'bottom, delimited from the body by a dashed line.'),
            # label=_(u'label_formmailer_body_footer',
                      # default=u'Body (signature)'),
            #),
        #),
    # BooleanField('showAll',
        # required=0,
        # searchable=0,
        # schemata='message',
        # default='1',
        # read_permission=ModifyPortalContent,
        # widget=BooleanWidget(
            #label=_(u'label_mailallfields_text', default=u"Include All Fields"),
            # description=_(u'help_mailallfields_text', default=u"""
                # Check this to include input for all fields
                #(except label and file fields). If you check
                # this, the choices in the pick box below
                # will be ignored.
                #"""),
            #),
        #),
    # LinesField('showFields',
        # required=0,
        # searchable=0,
        # schemata='message',
        # vocabulary='allFieldDisplayList',
        # read_permission=ModifyPortalContent,
        # widget=PicklistWidget(
            #label=_(u'label_mailfields_text', default=u"Show Responses"),
            # description=_(u'help_mailfields_text', default=u"""
                # Pick the fields whose inputs you'd like to include in
                # the e-mail.
                #"""),
            #),
        #),
    # BooleanField('includeEmpties',
        # required=0,
        # searchable=0,
        # schemata='message',
        # default='1',
        # read_permission=ModifyPortalContent,
        # widget=BooleanWidget(
            #label=_(u'label_mailEmpties_text', default=u"Include Empties"),
            # description=_(u'help_mailEmpties_text', default=u"""
                # Check this to include titles
                # for fields that received no input. Uncheck
                # to leave fields with no input out of the e-mail.
                #"""),
            #),
        #),
    # ZPTField('body_pt',
        # schemata='template',
        # write_permission=EDIT_TALES_PERMISSION,
        # default_method='getMailBodyDefault',
        # read_permission=ModifyPortalContent,
        # widget=TextAreaWidget(description=_(u'help_formmailer_body_pt',
            # default=u"""This is a Zope Page Template
            # used for rendering of the mail-body. You don\'t need to modify
            # it, but if you know TAL (Zope\'s Template Attribute Language)
            # you have the full power to customize your outgoing mails."""),
            #label=_(u'label_formmailer_body_pt', default=u'Mail-Body Template'),
            # rows=20,
            #visible={'edit': 'visible', 'view': 'invisible'},
            #),
        # validators=('zptvalidator',),
        #),
    # StringField('body_type',
        # schemata='template',
        # default_method='getMailBodyTypeDefault',
        # vocabulary=MIME_LIST,
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # read_permission=ModifyPortalContent,
        # widget=SelectionWidget(description=_(u'help_formmailer_body_type',
            # default=u"""Set the mime-type of the mail-body.
            # Change this setting only if you know exactly what you are doing.
            # Leave it blank for default behaviour."""),
            #label = _(u'label_formmailer_body_type', default=u'Mail Format'),
            #),
        #),
    # LinesField('xinfo_headers',
        # searchable=0,
        # required=0,
        # schemata='headers',
        # default_method='getDefaultXInfo',
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # read_permission=ModifyPortalContent,
        # vocabulary=DisplayList((
            #('HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR',),
            #('REMOTE_ADDR', 'REMOTE_ADDR',),
            #('PATH_INFO', 'PATH_INFO'),
            #('HTTP_USER_AGENT', 'HTTP_USER_AGENT',),
            #('HTTP_REFERER', 'HTTP_REFERER'),
            #), ),
        # widget=MultiSelectionWidget(
            #label=_(u'label_xinfo_headers_text', default=u'HTTP Headers'),
            # description=_(u'help_xinfo_headers_text', default=u"""
                # Pick any items from the HTTP headers that
                # you'd like to insert as X- headers in the
                # message.
                #"""),
            # format='checkbox',
            #),
        #),
    # LinesField('additional_headers',
        # schemata='headers',
        # searchable=0,
        # required=0,
        # default_method='getDefaultAddHdrs',
        # write_permission=EDIT_ADVANCED_PERMISSION,
        # read_permission=ModifyPortalContent,
        # widget=LinesWidget(
            #label=_(u'label_formmailer_additional_headers', default=u'Additional Headers'),
            # description=_(u'help_formmailer_additional_headers', default=u"""
                # Additional e-mail-header lines.
                # Only use RFC822-compliant headers.
                #"""),
            #),
        #),
    #))

# if gpg is not None:
    # formMailerAdapterSchema = formMailerAdapterSchema + Schema((
        # StringField('gpg_keyid',
            # schemata='encryption',
            # accessor='getGPGKeyId',
            # mutator='setGPGKeyId',
            # write_permission=USE_ENCRYPTION_PERMISSION,
            # read_permission=ModifyPortalContent,
            # widget=StringWidget(
                # description=_(u'help_gpg_key_id', default=u"""
                    # Give your key-id, e-mail address or
                    # whatever works to match a public key from current keyring.
                    # It will be used to encrypt the message body (not attachments).
                    # Contact the site administrator if you need to
                    # install a new public key.
                    # Note that you will probably wish to change your message
                    # template to plain text if you're using encryption.
                    # TEST THIS FEATURE BEFORE GOING PUBLIC!
                    #"""),
                #label=_(u'label_gpg_key_id', default=u'Key-Id'),
                #),
            #),
        #))


# formMailerAdapterSchema = formMailerAdapterSchema + Schema((
    # TALESString('subjectOverride',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True,  # just to hide from base view
        # widget=StringWidget(label=_(u'label_subject_override_text', default=u"Subject Expression"),
            # description=_(u'help_subject_override_text', default=u"""
                # A TALES expression that will be evaluated to override any value
                # otherwise entered for the e-mail subject header.
                # Leave empty if unneeded. Your expression should evaluate as a string.
                # PLEASE NOTE: errors in the evaluation of this expression will cause
                # an error on form display.
            #"""),
            # size=70,
        #),
    #),
    # TALESString('senderOverride',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True,  # just to hide from base view
        # widget=StringWidget(label=_(u'label_sender_override_text',
                                    # default=u"Sender Expression"),
            # description=_(u'help_sender_override_text', default=u"""
                # A TALES expression that will be evaluated to override the "From" header.
                # Leave empty if unneeded. Your expression should evaluate as a string.
                # PLEASE NOTE: errors in the evaluation of this expression will cause
                # an error on form display.
            #"""),
            # size=70,
        #),
    #),
    # TALESString('recipientOverride',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True,  # just to hide from base view
        # widget=StringWidget(label=_(u'label_recipient_override_text', default=u"Recipient Expression"),
            # description=_(u'help_recipient_override_text', default=u"""
                # A TALES expression that will be evaluated to override any value
                # otherwise entered for the recipient e-mail address. You are strongly
                # cautioned against using unvalidated data from the request for this purpose.
                # Leave empty if unneeded. Your expression should evaluate as a string.
                # PLEASE NOTE: errors in the evaluation of this expression will cause
                # an error on form display.
            #"""),
            # size=70,
        #),
    #),
    # TALESString('ccOverride',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True, # just to hide from base view
        # widget=StringWidget(label=_(u'label_cc_override_text', default=u"CC Expression"),
            # description=_(u'help_cc_override_text', default=u"""
                # A TALES expression that will be evaluated to override any value
                # otherwise entered for the CC list. You are strongly
                # cautioned against using unvalidated data from the request for this purpose.
                # Leave empty if unneeded. Your expression should evaluate as a sequence of strings.
                # PLEASE NOTE: errors in the evaluation of this expression will cause
                # an error on form display.
            #"""),
            # size=70,
        #),
    #),
    # TALESString('bccOverride',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True,  # just to hide from base view
        # widget=StringWidget(label=_(u'label_bcc_override_text', default=u"BCC Expression"),
            # description=_(u'help_bcc_override_text', default=u"""
                # A TALES expression that will be evaluated to override any value
                # otherwise entered for the BCC list. You are strongly
                # cautioned against using unvalidated data from the request for this purpose.
                # Leave empty if unneeded. Your expression should evaluate as a sequence of strings.
                # PLEASE NOTE: errors in the evaluation of this expression will cause
                # an error on form display.
            #"""),
            # size=70,
        #),
    #),

    # TALESString('smtp_envelope_mail_from_override',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True, # just to hide from base view
        # widget=StringWidget(label=\
                            #_(u'label_envelope_from_address_averride_text',
                              # default=(u"SMTP Envelope MAIL FROM address "
                                       #"Expression")),
                           # description=_(
                # u'help_envelope_from_address_averride_text', default=u"""
                # A TALES expression that will be evaluated to override any value
                # otherwise entered for the 'SMTP Envelope MAIL FROM address'
                # field. You are strongly cautioned against using unvalidated data
                # from the request for this purpose. Leave empty if unneeded.
                # Your expression should evaluate as a sequence of strings.
                # PLEASE NOTE: errors in the evaluation of this expression
                # will cause an error on form display.
            #"""),
            # size=70,
        #),
    #),
    #))


default_script = u"""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=
##

# Available parameters:
#  fields  = HTTP request form fields as key value pairs
#  request = The current HTTP request.
#            Access fields by request.form["myfieldname"]
#  ploneformgen = PloneFormGen object
#
# Return value is not processed -- unless you
# return a dictionary with contents. That's regarded
# as an error and will stop processing of actions
# and return the user to the form. Error dictionaries
# should be of the form {'field_id':'Error message'}


assert False, "Please complete your script"

"""

getProxyRoleChoices = SimpleVocabulary.fromItems((
    (u"No proxy role", u"none"),
    (u"Manager", u"Manager"),
))


class ICustomScript(form.Schema, IAction):

    """Executes a Python script for form data"""
    form.fieldset(u"overrides", label="Overrides", fields=['execCondition'])
    form.omitted('order', 'default', 'missing_value', 'readonly')
    # Field represents Form Mailer."""
    form.read_permission(ProxyRole='cmf.ModifyPortalContent')
    form.write_permission(ProxyRole='cmf.ModifyPortalContent')
    ProxyRole = zs.Choice(
        title=_(u'label_script_proxy', default=u'Proxy role'),
        description=_(u'help_script_proxy',
                      default=u"Role under which to run the script."),
        default=u"none",
        required=True,
        vocabulary=getProxyRoleChoices,
    )
    # TODO PythonField('ScriptBody',
    form.read_permission(ScriptBody='cmf.ModifyPortalContent')
    form.write_permission(ScriptBody='cmf.ModifyPortalContent')
    ScriptBody = zs.Text(
        title=_(u'label_script_body', default=u'Script body'),
        description=_(u'help_script_body', default=u"Write your script here."),
        default=default_script,
        required=False,
    )


class ISaveData(form.Schema, IAction):

    """A form action adapter that will save form input data and
       return it in csv- or tab-delimited format."""
    form.fieldset(u"overrides", label="Overrides", fields=['execCondition'])
    form.omitted('order', 'default', 'missing_value', 'readonly')
        # LinesField('showFields',
            # required=0,
            # searchable=0,
            # vocabulary='allFieldDisplayList',
            # widget=PicklistWidget(
                #label=_(u'label_savefields_text', default=u"Saved Fields"),
                # description=_(u'help_savefields_text', default=u"""
                    # Pick the fields whose inputs you'd like to include in
                    # the saved data. If empty, all fields will be saved.
                    #"""),
                #),
            #),
        # LinesField('ExtraData',
            # widget=MultiSelectionWidget(
                #label=_(u'label_savedataextra_text', default='Extra Data'),
                # description=_(u'help_savedataextra_text', default=u"""
                    # Pick any extra data you'd like saved with the form input.
                    #"""),
                # format='checkbox',
                #),
            # vocabulary='vocabExtraDataDL',
            #),
        # StringField('DownloadFormat',
            # searchable=0,
            # required=1,
            # default='csv',
            # vocabulary='vocabFormatDL',
            # widget=SelectionWidget(
                #label=_(u'label_downloadformat_text', default=u'Download Format'),
                #),
            #),
        # BooleanField("UseColumnNames",
            # required=False,
            # searchable=False,
            # widget=BooleanWidget(
                #label=_(u'label_usecolumnnames_text', default=u"Include Column Names"),
                #description=_(u'help_usecolumnnames_text', default=u"Do you wish to have column names on the first line of downloaded input?"),
                #),
            #),
        # ExLinesField('SavedFormInput',
            # edit_accessor='getSavedFormInputForEdit',
            # mutator='setSavedFormInput',
            # searchable=0,
            # required=0,
            # primary=1,
            #schemata="saved data",
            # read_permission=DOWNLOAD_SAVED_PERMISSION,
            # widget=TextAreaWidget(
                #label=_(u'label_savedatainput_text', default=u"Saved Form Input"),
                # description=_(u'help_savedatainput_text'),
                #),
            #),


class IMailerWidget(interfaces.IWidget):

    """Mailer widget."""
