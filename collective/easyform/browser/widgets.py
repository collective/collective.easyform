# -*- coding: utf-8 -*-

import zope.component
import zope.interface
import zope.schema.interfaces

from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from collective.easyform.interfaces import ILabelWidget
from collective.easyform.interfaces import IRichLabelWidget


@zope.interface.implementer_only(ILabelWidget)
class LabelWidget(widget.HTMLFormElement, Widget):

    """Textarea widget implementation."""

    klass = u'label-widget'
    css = u'label'
    value = u''

    def update(self):
        super(LabelWidget, self).update()
        widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def LabelFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, LabelWidget(request))


@zope.interface.implementer_only(IRichLabelWidget)
class RichLabelWidget(widget.HTMLFormElement, Widget):

    """Textarea widget implementation."""

    klass = u'rich-label-widget'
    css = u'richlabel'
    value = u''

    def update(self):
        super(RichLabelWidget, self).update()
        widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def RichLabelFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, RichLabelWidget(request))


class LabelRenderWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('label.pt')


class RichLabelRenderWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('rich_label.pt')
