# -*- coding: utf-8 -*-

from .actions import IAction  # noqa
from .actions import IActionEditForm  # noqa
from .actions import IActionExtender  # noqa
from .actions import IActionFactory  # noqa
from .actions import IEasyFormActionContext  # noqa
from .actions import IEasyFormActionsContext  # noqa
from .actions import IEasyFormActionsEditorExtender  # noqa
from .actions import INewAction  # noqa
from .customscript import ICustomScript  # noqa
from .easyform import IEasyForm  # noqa
from .easyform import IEasyFormImportFormSchema  # noqa
from .easyform import IEasyFormThanksPage  # noqa
from .fields import IEasyFormFieldContext  # noqa
from .fields import IEasyFormFieldsContext  # noqa
from .fields import IEasyFormFieldsEditorExtender  # noqa
from .fields import IFieldExtender  # noqa
from .fields import IFieldValidator  # noqa
from .fields import ILabel  # noqa
from .fields import ILabelWidget  # noqa
from .fields import INorobotCaptcha  # noqa
from .fields import IReCaptcha  # noqa
from .fields import IRichLabel  # noqa
from .fields import IRichLabelWidget  # noqa
from .layer import IEasyFormLayer  # noqa
from .mailer import IMailer  # noqa
from .savedata import IExtraData  # noqa
from .savedata import ISaveData  # noqa
from .savedata import ISavedDataFormWrapper  # noqa
from zope.interface import Interface


class IEasyFormView(Interface):

    """
    EasyForm view interface
    """


class IEasyFormForm(Interface):

    """
    EasyForm view interface
    """
