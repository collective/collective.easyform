# -*- coding: utf-8 -*-

from collective.easyform.interfaces import ILabelWidget
from collective.easyform.interfaces import IRichLabelWidget
from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField


@implementer_only(ILabelWidget)
class LabelWidget(widget.HTMLFormElement, Widget):

    """Textarea widget implementation."""

    klass = u"label-widget"
    css = u"label"
    value = u""

    def update(self):
        super(LabelWidget, self).update()
        widget.addFieldClass(self)


@adapter(IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def LabelFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, LabelWidget(request))


@implementer_only(IRichLabelWidget)
class RichLabelWidget(widget.HTMLFormElement, Widget):

    """Textarea widget implementation."""

    klass = u"rich-label-widget"
    css = u"richlabel"
    value = u""

    def update(self):
        super(RichLabelWidget, self).update()
        widget.addFieldClass(self)


@adapter(IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def RichLabelFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, RichLabelWidget(request))


class LabelRenderWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile("label.pt")


class RichLabelRenderWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile("rich_label.pt")
