# -*- coding: utf-8 -*-
from collections import namedtuple
from lxml import etree
from Products.PloneFormGen.content.fields import FGFieldsetEnd
from Products.PloneFormGen.content.fields import FGFieldsetStart
from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.interfaces import IPloneFormGenFieldset

import logging
import six


logger = logging.getLogger('collective.easyform.migration')


NAMESPACES = {
    'easyform': 'http://namespaces.plone.org/supermodel/easyform',
    'form': 'http://namespaces.plone.org/supermodel/form',
}


def append_field(schema, type_, name, properties):
    field = etree.SubElement(schema, u'field')
    field.set(u'name', name)
    field.set(u'type', type_)
    return field


def append_label_field(schema, type_, name, properties):
    field = append_field(schema, type_, name, properties)
    append_node(field, u'required', u'False')
    return field


def append_date_field(schema, type_, name, properties):
    if properties.get('fgShowHM', False):
        return append_field(schema, u'zope.schema.Datetime', name, properties)
    else:
        return append_field(schema, u'zope.schema.Date', name, properties)


def append_fieldset(schema, type_, name, properties):
    fieldset = etree.SubElement(schema, u'fieldset')
    fieldset.set(u'name', name)
    return fieldset


def set_attribute(field, name, value):
    if u':' in name:
        ns, attr = name.split(':')
        ns = NAMESPACES.get(ns, ns)
        field.set(u'{{{}}}{}'.format(ns, attr), value)
    else:
        field.set(name, value)


def append_node(field, name, value):
    if ':' in name:
        ns, name = name.split(':')
        ns = NAMESPACES.get(ns, ns)
        name = '{{{}}}{}'.format(ns, name)
    node = etree.SubElement(field, name)
    if isinstance(value, (list, tuple)):
        value = u' '.join(value)
    node.text = value
    return node


def append_list_node(field, name, value):
    node = append_node(field, name, None)
    for val in value:
        el = etree.SubElement(node, 'element')
        if '|' in val:
            key, val = val.split('|')
            el.set('key', key)
        el.text = val


def append_required_node(field, name, value):
    if value == u'False':
        append_node(field, name, value)


def append_maxlength_node(field, name, value):
    if value != u'0':
        append_node(field, name, value)


def append_vocab_node(field, name, value):
    if field.get('type') == 'zope.schema.Set':
        node = etree.SubElement(field, 'value_type')
        node.set('type', 'zope.schema.Choice')
    else:
        node = field

    append_list_node(node, u'values', value)


def append_default_node(field, name, value):
    if isinstance(value, list):
        return
    if field.get('type') == 'collective.easyform.fields.RichLabel':
        append_node(field, 'rich_label', value)
    else:
        append_node(field, name, value)


def append_widget_node(field, name, value):
    node = append_node(field, name, None)
    type_ = field.get('type')
    if type_ == 'zope.schema.Set':
        if value == 'select':
            widget = 'z3c.form.browser.select.CollectionSelectFieldWidget'
        else:
            widget = 'z3c.form.browser.checkbox.CheckBoxFieldWidget'
    else:
        if value == 'select':
            widget = 'z3c.form.browser.select.ChoiceWidgetDispatcher'
        else:
            widget = 'z3c.form.browser.radio.RadioFieldWidget'
    set_attribute(node, 'type', widget)


def append_or_set_title(field, name, value):
    if field.tag == 'fieldset':
        set_attribute(field, 'label', value)
    else:
        append_node(field, name, value)


def convert_tales_expressions(value):
    if value == u'here/memberEmail':
        return u"python:member and member.getProperty('email', '') or ''"
    elif value == u'here/memberFullName':
        return u"python:member and member.getProperty('fullname', '') or ''"
    elif value == u'here/memberId':
        return u"python:member and member.id or ''"
    return value


def to_text(value):
    if isinstance(value, (list, tuple)):
        return [to_text(v) for v in value]
    value = str(value)
    if six.PY2:
        value = value.decode('utf8')
    return value


Type = namedtuple('Type', ['name', 'handler'])
Property = namedtuple('Property', ['name', 'handler'])

TYPES_MAPPING = {
    'FormStringField': Type('zope.schema.TextLine', append_field),
    'FormPasswordField': Type('zope.schema.Password', append_field),
    'FormIntegerField': Type('zope.schema.Int', append_field),
    'FormFixedPointField': Type('zope.schema.Float', append_field),
    'FormBooleanField': Type('zope.schema.Bool', append_field),
    'FormDateField': Type('zope.schema.Date', append_date_field),
    'FormLabelField': Type('collective.easyform.fields.Label', append_label_field),
    'FormLinesField': Type('zope.schema.Text', append_field),
    'FormSelectionField': Type('zope.schema.Choice', append_field),
    'FormMultiSelectionField': Type('zope.schema.Set', append_field),
    'FormTextField': Type('zope.schema.Text', append_field),
    'FormRichTextField': Type('plone.app.textfield.RichText', append_field),
    'FormRichLabelField': Type('collective.easyform.fields.RichLabel', append_label_field),
    'FormFileField': Type('plone.namedfile.field.NamedBlobFile', append_field),
    'FormCaptchaField': Type('collective.easyform.fields.ReCaptcha', append_field),
    'FieldsetStart': Type('', append_fieldset),
    'FieldsetEnd': Type('', None),
}

PROPERTIES_MAPPING = {
    'description': Property('description', append_node),
    'fgDefault': Property('default', append_default_node),
    'fgmaxlength': Property('max_length', append_maxlength_node),
    'fgsize': None,  # Not available in collective.easyform
    'fgStringValidator': Property('easyform:validators', set_attribute),
    'fgTDefault': Property('easyform:TDefault', set_attribute),
    'fgTEnabled': Property('easyform:TEnabled', set_attribute),
    'fgTValidator': Property('easyform:TValidator', set_attribute),
    'fgTVocabulary': None,  # Not available in collective.easyform
    'fgVocabulary': Property('values', append_vocab_node),
    'hidden': Property('easyform:THidden', set_attribute),
    'maxval': Property('max', append_node),
    'minval': Property('min', append_node),
    'placeholder': None,  # Not available in collective.easyform
    'required': Property('required', append_required_node),
    'serverSide': Property('easyform:serverSide', set_attribute),
    'title': Property('title', append_or_set_title),
    'fgFormat': Property('form:widget', append_widget_node),
}


def pfg_fields_properties(obj):
    id_ = obj.getId()
    props = {}
    props['_portal_type'] = obj.portal_type
    for field in obj.Schema().fields():
        name = field.getName()
        accessor = field.getEditAccessor(obj)
        props[name] = accessor()
    return (id_, props)


def pfg_fields(context):
    fields = []
    for obj in context.objectValues():
        if IPloneFormGenFieldset.providedBy(obj):
            # handle FieldsetFolder folderish type
            parent = obj.aq_parent
            obj_id = obj.getId()
            # append a FieldsetStart field with title and description
            start = FGFieldsetStart(obj_id).__of__(parent)
            start.setTitle(obj.Title())
            start.setDescription(obj.Description())
            fields.append(pfg_fields_properties(start))
            # add all the fieldset contained fields
            fields.extend(pfg_fields(obj))
            # finish by appending a marker FieldsetEnd field
            end = FGFieldsetEnd(obj_id).__of__(parent)
            fields.append(pfg_fields_properties(end))
            continue
        if not isinstance(obj, BaseFormField):
            continue
        fields.append(pfg_fields_properties(obj))
    return fields


def fields_model(ploneformgen):
    """Create a fields xml model from a PloneFormGen instance."""
    parser = etree.XMLParser(remove_blank_text=True)
    model = etree.fromstring(FIELDS_MODEL, parser)
    schema = model.find(
        '{http://namespaces.plone.org/supermodel/schema}schema')
    for fieldname, properties in pfg_fields(ploneformgen):
        portal_type = properties['_portal_type']
        if portal_type == 'FieldsetEnd':
            schema = schema.getparent()
            continue

        type_ = TYPES_MAPPING.get(portal_type)
        if type_ is None:
            logger.warning(
                "Ingoring field '%s' of type '%s'.", fieldname, portal_type)
            continue

        if type_.handler is None:
            continue
        field = type_.handler(schema, type_.name, fieldname, properties)

        for name, value in properties.items():
            prop = PROPERTIES_MAPPING.get(name)
            if prop is None:
                continue

            value = to_text(value)

            # Convert TALES expressions with PFG specific methods
            if name.startswith('fgT'):
                value = convert_tales_expressions(value)

            prop.handler(field, prop.name, value)

        if portal_type == 'FieldsetStart':
            schema = field

    return etree.tostring(model, pretty_print=True)


FIELDS_MODEL = b"""
<model
    xmlns="http://namespaces.plone.org/supermodel/schema"
    xmlns:easyform="http://namespaces.plone.org/supermodel/easyform"
    xmlns:i18n="http://xml.zope.org/namespaces/i18n"
    i18n:domain="collective.easyform">
  <schema></schema>
</model>
"""
