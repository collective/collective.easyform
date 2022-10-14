# -*- coding: utf-8 -*-
from .actions import IAction
from collective.easyform import easyformMessageFactory as _
from plone.autoform import directives
from plone.z3cform.interfaces import IFormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.interface import Interface

import zope.interface
import zope.schema.interfaces


class ISavedDataFormWrapper(IFormWrapper):
    pass


class IExtraData(Interface):
    dt = zope.schema.TextLine(
        title=_("Posting Date/Time"), required=False, default="", missing_value=""
    )
    HTTP_X_FORWARDED_FOR = zope.schema.TextLine(
        title=_(
            "extra_header",
            default="${name} Header",
            mapping={"name": "HTTP_X_FORWARDED_FOR"},
        ),
        required=False,
        default="",
        missing_value="",
    )
    REMOTE_ADDR = zope.schema.TextLine(
        title=_(
            "extra_header",
            default="${name} Header",
            mapping={"name": "REMOTE_ADDR"},
        ),
        required=False,
        default="",
        missing_value="",
    )
    HTTP_USER_AGENT = zope.schema.TextLine(
        title=_(
            "extra_header",
            default="${name} Header",
            mapping={"name": "HTTP_USER_AGENT"},
        ),
        required=False,
        default="",
        missing_value="",
    )


class ISaveData(IAction):

    """A form action adapter that will save form input data and
    return it in csv- or tab-delimited format."""

    showFields = zope.schema.List(
        title=_("label_savefields_text", default="Saved Fields"),
        description=_(
            "help_savefields_text",
            default="Pick the fields whose inputs you'd like to include in "
            "the saved data. If empty, all fields will be saved.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Fields"),
    )
    directives.widget(ExtraData=CheckBoxFieldWidget)
    ExtraData = zope.schema.List(
        title=_("label_savedataextra_text", default="Extra Data"),
        description=_(
            "help_savedataextra_text",
            default="Pick any extra data you'd like saved with the form " "input.",
        ),
        unique=True,
        value_type=zope.schema.Choice(vocabulary="easyform.ExtraDataDL"),
    )
    DownloadFormat = zope.schema.Choice(
        title=_("label_downloadformat_text", default="Download Format"),
        default="csv",
        vocabulary="easyform.FormatDL",
    )
    UseColumnNames = zope.schema.Bool(
        title=_("label_usecolumnnames_text", default="Include Column Names"),
        description=_(
            "help_usecolumnnames_text",
            default="Do you wish to have column names on the first line of "
            "downloaded input?",
        ),
        default=True,
        required=False,
    )
