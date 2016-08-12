from plone.schemaeditor.interfaces import IEditableSchema
from Products.CMFPlone.utils import safe_unicode

import types
import zope.schema

# Get all the PFG forms present in the site.
# PFG_Forms = api.content.find(context=api.portal.get(), portal_type='FormFolder')
#
# TODO: change the field factory lookup to an adaptor mechanism


def setTaggedValue(schema, tag, fieldname, value):
    # tagged values are a mechanism for adding non-standard items to a field interface.
    # they are actually stored in the schema, not the schema field.
    data = schema.queryTaggedValue(tag, {})
    data[fieldname] = value
    schema.setTaggedValue(tag, data)


def setSimpleAttributeFromAccessor(sfield, pfg_field, attribute_name, accessor_id):
    # check to see if a pfg form field has a particular property accessor.
    # if it does, use it to set a schema field attribute

    accessor = getattr(pfg_field, accessor_id, None)
    if accessor is not None:
        value = accessor()
        if isinstance(value, types.StringTypes):
            value = safe_unicode(value)
        setattr(sfield, attribute_name, value)


def setIntAttributeFromAccessor(sfield, pfg_field, attribute_name, accessor_id):
    # check to see if a pfg form field has a particular property accessor.
    # if it does, use it to set a schema field attribute

    accessor = getattr(pfg_field, accessor_id, None)
    if accessor is not None:
        value = accessor()
        if isinstance(value, types.StringTypes):
            value = int(value)
        setattr(sfield, attribute_name, value)


def setBaseFieldAttributes(schema, pfg_field, tl, name):
    # Set common schema attributes
    tl.__name__ = name
    tl.title = safe_unicode(pfg_field.title)
    setSimpleAttributeFromAccessor(tl, pfg_field, 'required', 'getDescription')
    setSimpleAttributeFromAccessor(tl, pfg_field, 'required', 'getRequired')
    setIntAttributeFromAccessor(tl, pfg_field, 'max_length', 'getRawFgmaxlength')
    setSimpleAttributeFromAccessor(tl, pfg_field, 'default', 'getFgDefault')
    # set tagged values that are not standard schema attributes
    setTaggedValue(schema, 'TDefault', name, pfg_field.getRawFgTDefault())
    setTaggedValue(schema, 'TEnabled', name, pfg_field.getRawFgTEnabled())
    setTaggedValue(schema, 'TValidator', name, pfg_field.getRawFgTValidator())
    setTaggedValue(schema, 'serverSide', name, bool(pfg_field.getRawServerSide()))


def add_pfg_string_field_to_schema(schema, pfg_string_field, name):
    tl = zope.schema.TextLine()
    IEditableSchema(schema).addField(tl, name=name)
    setBaseFieldAttributes(schema, pfg_string_field, tl, name)
    setTaggedValue(schema, 'validators', name, [pfg_string_field.getRawFgStringValidator()])


def add_pfg_text_field_to_schema(schema, pfg_field, name):
    tl = zope.schema.Text()
    IEditableSchema(schema).addField(tl, name=name)
    setBaseFieldAttributes(schema, pfg_field, tl, name)
    if getattr(tl, 'max_length', None) == 0:
        tl.max_length = None


def add_pfg_int_field_to_schema(schema, pfg_field, name):
    tl = zope.schema.Int()
    IEditableSchema(schema).addField(tl, name=name)
    setBaseFieldAttributes(schema, pfg_field, tl, name)


fieldFactories = dict(
    FormStringField=add_pfg_string_field_to_schema,
    FormTextField=add_pfg_text_field_to_schema,
    FormIntegerField=add_pfg_int_field_to_schema,
)


def add_pfg_field_to_schema(schema, pfg_field, name):
    my_factory = fieldFactories.get(pfg_field.portal_type)
    if my_factory is None:
        # log the fact that we can't handle this field.
        # but, until we support that...
        raise AssertionError('Unsupported PloneFormGen Field Type: {}'.format(pfg_field.portal_type))
    else:
        my_factory(schema, pfg_field, name)
