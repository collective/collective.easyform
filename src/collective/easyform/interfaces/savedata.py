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
        title=_(u"Posting Date/Time"), required=False, default=u"", missing_value=u""
    )
    HTTP_X_FORWARDED_FOR = zope.schema.TextLine(
        title=_(
            u"extra_header",
            default=u"${name} Header",
            mapping={u"name": u"HTTP_X_FORWARDED_FOR"},
        ),
        required=False,
        default=u"",
        missing_value=u"",
    )
    REMOTE_ADDR = zope.schema.TextLine(
        title=_(
            u"extra_header",
            default=u"${name} Header",
            mapping={u"name": u"REMOTE_ADDR"},
        ),
        required=False,
        default=u"",
        missing_value=u"",
    )
    HTTP_USER_AGENT = zope.schema.TextLine(
        title=_(
            u"extra_header",
            default=u"${name} Header",
            mapping={u"name": u"HTTP_USER_AGENT"},
        ),
        required=False,
        default=u"",
        missing_value=u"",
    )


class ISaveData(IAction):

    """A form action adapter that will save form input data and
       return it in csv- or tab-delimited format."""

    showFields = zope.schema.List(
        title=_(u"label_savefields_text", default=u"Saved Fields"),
        description=_(
            u"help_savefields_text",
            default=u"Pick the fields whose inputs you'd like to include in "
            u"the saved data. If empty, all fields will be saved.",
        ),
        unique=True,
        required=False,
        value_type=zope.schema.Choice(vocabulary="easyform.Fields"),
    )
    directives.widget(ExtraData=CheckBoxFieldWidget)
    ExtraData = zope.schema.List(
        title=_(u"label_savedataextra_text", default="Extra Data"),
        description=_(
            u"help_savedataextra_text",
            default=u"Pick any extra data you'd like saved with the form " u"input.",
        ),
        unique=True,
        value_type=zope.schema.Choice(vocabulary="easyform.ExtraDataDL"),
    )
    DownloadFormat = zope.schema.Choice(
        title=_(u"label_downloadformat_text", default=u"Download Format"),
        default=u"csv",
        vocabulary="easyform.FormatDL",
    )
    UseColumnNames = zope.schema.Bool(
        title=_(u"label_usecolumnnames_text", default=u"Include Column Names"),
        description=_(
            u"help_usecolumnnames_text",
            default=u"Do you wish to have column names on the first line of "
            u"downloaded input?",
        ),
        default=True,
        required=False,
    )
