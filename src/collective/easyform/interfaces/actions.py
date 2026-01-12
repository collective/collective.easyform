from .validators import isTALES
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _  # NOQA
from plone.autoform import directives
from plone.schemaeditor.interfaces import ID_RE
from plone.schemaeditor.interfaces import IFieldContext
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.schemaeditor.interfaces import ISchemaContext
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema

import z3c.form.interfaces
import zope.interface
import zope.schema.interfaces


try:
    from plone.schemaeditor import SchemaEditorMessageFactory as __  # NOQA
except ImportError:
    from plone.schemaeditor import _ as __


MODIFY_PORTAL_CONTENT = "cmf.ModifyPortalContent"


class IEasyFormActionsEditorExtender(IFieldEditorExtender):
    pass


def isValidFieldName(value):
    if not ID_RE.match(value):
        raise zope.interface.Invalid(
            __("Please use only letters, numbers and " "the following characters: _.")
        )
    return True


class INewAction(Schema):

    title = zope.schema.TextLine(title=__("Title"), required=True)

    __name__ = zope.schema.ASCIILine(
        title=__("Short Name"),
        description=__("Used for programmatic access to the field."),
        required=True,
        constraint=isValidFieldName,
    )

    factory = zope.schema.Choice(
        title=_("Action type"), vocabulary="EasyFormActions", required=True
    )

    @zope.interface.invariant
    def checkTitleTypes(data):
        if data.__name__ is not None and data.factory is not None:
            if (
                data.__name__ == "title"
                and data.factory.fieldcls is not zope.schema.TextLine
            ):
                raise zope.interface.Invalid(
                    __("The 'title' field must be a Text line (string) " "field.")
                )


class IActionFactory(zope.schema.interfaces.IField):
    """A component that instantiates a action when called."""

    title = zope.schema.TextLine(title=__("Title"))


class IEasyFormActionsContext(ISchemaContext):
    """EasyForm actions view interface."""


class IActionExtender(Schema):
    fieldset("overrides", label=_("Overrides"), fields=["execCondition"])
    directives.read_permission(execCondition=MODIFY_PORTAL_CONTENT)
    directives.write_permission(execCondition=config.EDIT_TALES_PERMISSION)
    execCondition = zope.schema.TextLine(
        title=_("label_execcondition_text", default="Execution Condition"),
        description=_(
            "help_execcondition_text",
            default="A TALES expression that will be evaluated to determine "
            "whether or not to execute this action. Leave empty if "
            "unneeded, and the action will be executed. Your "
            "expression should evaluate as a boolean; return True "
            "if you wish the action to execute. PLEASE NOTE: errors "
            "in the evaluation of this expression will  cause an "
            "error on form display.",
        ),
        default="",
        constraint=isTALES,
        required=False,
    )


class IEasyFormActionContext(IFieldContext):
    """EasyForm action content marker."""


class IActionEditForm(z3c.form.interfaces.IEditForm):
    """Marker interface for action edit forms."""


class IAction(Schema, zope.schema.interfaces.IField):
    directives.omitted(
        "description", "required", "order", "default", "missing_value", "readonly"
    )
    #     required = zope.schema.Bool(
    #         title=_('Enabled'),
    #        description=_('Tells whether a action is enabled.'),
    #         default=True)

    def onSuccess(fields, request):  # NOQA
        pass
