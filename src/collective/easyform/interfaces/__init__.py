# -*- coding: utf-8 -*-
from collective.easyform.interfaces.actions import IAction  # noqa
from collective.easyform.interfaces.actions import IActionEditForm  # noqa
from collective.easyform.interfaces.actions import IActionExtender  # noqa
from collective.easyform.interfaces.actions import IActionFactory  # noqa
from collective.easyform.interfaces.actions import IEasyFormActionContext  # noqa
from collective.easyform.interfaces.actions import IEasyFormActionsContext  # noqa
from collective.easyform.interfaces.actions import IEasyFormActionsEditorExtender  # noqa
from collective.easyform.interfaces.actions import INewAction  # noqa
from collective.easyform.interfaces.customscript import ICustomScript  # noqa
from collective.easyform.interfaces.easyform import IEasyForm  # noqa
from collective.easyform.interfaces.easyform import IEasyFormImportFormSchema  # noqa
from collective.easyform.interfaces.fields import IEasyFormFieldContext  # noqa
from collective.easyform.interfaces.fields import IEasyFormFieldsContext  # noqa
from collective.easyform.interfaces.fields import IEasyFormFieldsEditorExtender  # noqa
from collective.easyform.interfaces.fields import IFieldExtender  # noqa
from collective.easyform.interfaces.fields import IFieldValidator  # noqa
from collective.easyform.interfaces.fields import ILabel  # noqa
from collective.easyform.interfaces.fields import ILabelWidget  # noqa
from collective.easyform.interfaces.fields import IReCaptcha  # noqa
from collective.easyform.interfaces.fields import IRichLabel  # noqa
from collective.easyform.interfaces.fields import IRichLabelWidget  # noqa
from collective.easyform.interfaces.mailer import IMailer  # noqa
from collective.easyform.interfaces.savedata import IExtraData  # noqa
from collective.easyform.interfaces.savedata import ISaveData  # noqa
from collective.easyform.interfaces.savedata import ISavedDataFormWrapper  # noqa
from plone.app.z3cform.interfaces import IPloneFormLayer
from zope.interface import Interface


class IEasyFormView(Interface):

    """
    EasyForm view interface
    """


class IEasyFormForm(Interface):

    """
    EasyForm view interface
    """


class IEasyFormLayer(IPloneFormLayer):
    """Browserlayer for EasyForm
    """


class IEasyFormFormLayer(IEasyFormLayer):
    """Browserlayer for EasyForm
    """
