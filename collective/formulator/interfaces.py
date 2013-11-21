from zope.interface import Invalid, Interface, invariant
from zope import schema as zs
from zope.schema.interfaces import IField
from z3c.form import interfaces

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
    # title = zs.TextLine(
        # title=zs.interfaces.ITextLine['title'].title,
        # description=zs.interfaces.ITextLine['title'].description,
        # default=u"",
        # required=True,
        #)
    required = zs.Bool(
        title=_("Enabled"),
        description=_("Tells whether a action is enabled."),
        default=True)
    # TALESString('execCondition',
        # schemata='overrides',
        # searchable=0,
        # required=0,
        # validators=('talesvalidator',),
        # default='',
        # write_permission=EDIT_TALES_PERMISSION,
        # read_permission=ModifyPortalContent,
        # isMetadata=True,  # just to hide from base view
        # widget=StringWidget(label=_(u'label_execcondition_text', default=u"Execution Condition"),
            # description=_(u'help_execcondition_text', default=u"""
                # A TALES expression that will be evaluated to determine whether or not
                # to execute this action.
                # Leave empty if unneeded, and the action will be executed.
                # Your expression should evaluate as a boolean; return True if you wish
                # the action to execute.
                # PLEASE NOTE: errors in the evaluation of this expression will cause
                # an error on form display.
            #"""),
            # size=70,
        #),
    #),
    # TODO: TALESString zope schema field
    execCondition = zs.TextLine(
        title=_(u"Execution Condition"),
        description=(
            _(u"A TALES expression that will be evaluated to determine whether"
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

    """Field represents Form Mailer."""
    form.fieldset(u"overrides", label="Overrides", fields=['execCondition'])
    form.omitted('order', 'default', 'missing_value', 'readonly')


class IMailerWidget(interfaces.IWidget):

    """Mailer widget."""
