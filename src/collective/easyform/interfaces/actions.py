# -*- coding: utf-8 -*-
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
            __(u"Please use only letters, numbers and " u"the following characters: _.")
        )
    return True


class INewAction(Schema):

    title = zope.schema.TextLine(title=__(u"Title"), required=True)

    __name__ = zope.schema.ASCIILine(
        title=__(u"Short Name"),
        description=__(u"Used for programmatic access to the field."),
        required=True,
        constraint=isValidFieldName,
    )

    factory = zope.schema.Choice(
        title=_(u"Action type"), vocabulary="EasyFormActions", required=True
    )

    @zope.interface.invariant
    def checkTitleTypes(data):
        if data.__name__ is not None and data.factory is not None:
            if (
                data.__name__ == "title"
                and data.factory.fieldcls is not zope.schema.TextLine
            ):
                raise zope.interface.Invalid(
                    __(u"The 'title' field must be a Text line (string) " u"field.")
                )


class IActionFactory(zope.schema.interfaces.IField):
    """A component that instantiates a action when called."""

    title = zope.schema.TextLine(title=__(u"Title"))


class IEasyFormActionsContext(ISchemaContext):
    """EasyForm actions view interface."""


class IActionExtender(Schema):
    fieldset(u"overrides", label=_("Overrides"), fields=["execCondition"])
    directives.read_permission(execCondition=MODIFY_PORTAL_CONTENT)
    directives.write_permission(execCondition=config.EDIT_TALES_PERMISSION)
    execCondition = zope.schema.TextLine(
        title=_(u"label_execcondition_text", default=u"Execution Condition"),
        description=_(
            u"help_execcondition_text",
            default=u"A TALES expression that will be evaluated to determine "
            u"whether or not to execute this action. Leave empty if "
            u"unneeded, and the action will be executed. Your "
            u"expression should evaluate as a boolean; return True "
            u"if you wish the action to execute. PLEASE NOTE: errors "
            u"in the evaluation of this expression will  cause an "
            u"error on form display.",
        ),
        default=u"",
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
