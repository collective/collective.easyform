# -*- coding: utf-8 -*-

from actions import IAction  # NOQA
from actions import IActionEditForm  # NOQA
from actions import IActionExtender  # NOQA
from actions import IActionFactory  # NOQA
from actions import IEasyFormActionContext  # NOQA
from actions import IEasyFormActionsContext  # NOQA
from actions import IEasyFormActionsEditorExtender  # NOQA
from actions import INewAction  # NOQA
from customscript import ICustomScript  # NOQA
from easyform import IEasyForm  # NOQA
from easyform import IEasyFormImportFormSchema  # NOQA
from fields import IEasyFormFieldContext  # NOQA
from fields import IEasyFormFieldsContext  # NOQA
from fields import IEasyFormFieldsEditorExtender  # NOQA
from fields import IFieldExtender  # NOQA
from fields import IFieldValidator  # NOQA
from fields import ILabel  # NOQA
from fields import ILabelWidget  # NOQA
from fields import IReCaptcha  # NOQA
from fields import IRichLabel  # NOQA
from fields import IRichLabelWidget  # NOQA
from mailer import IMailer  # NOQA
from savedata import IExtraData  # NOQA
from savedata import ISaveData  # NOQA
from savedata import ISavedDataFormWrapper  # NOQA
from zope.interface import Interface


class IEasyFormView(Interface):

    """
    EasyForm view interface
    """


class IEasyFormForm(Interface):

    """
    EasyForm view interface
    """
