from plone.schemaeditor.interfaces import IEditableSchema
from Products.CMFPlone.utils import safe_unicode

import types
import zope.schema


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
            if len(value):
                value = int(value)
            else:
                value = 0
        setattr(sfield, attribute_name, value)


def setBaseFieldAttributes(schema, pfg_field, tl, name):
    # Set common schema attributes
    tl.__name__ = name
    tl.title = safe_unicode(pfg_field.title)
    setSimpleAttributeFromAccessor(tl, pfg_field, 'required', 'getDescription')
    setSimpleAttributeFromAccessor(tl, pfg_field, 'required', 'getRequired')
    setIntAttributeFromAccessor(tl, pfg_field, 'max_length', 'getRawFgmaxlength')
    if getattr(tl, 'max_length', None) == 0:
        tl.max_length = None
    # set tagged values that are not standard schema attributes
    setTaggedValue(schema, 'TDefault', name, pfg_field.getRawFgTDefault())
    setTaggedValue(schema, 'TEnabled', name, pfg_field.getRawFgTEnabled())
    setTaggedValue(schema, 'TValidator', name, pfg_field.getRawFgTValidator())
    get_raw_server_side = getattr(pfg_field, 'getRawServerSide', None)
    if get_raw_server_side is not None:
        setTaggedValue(schema, 'serverSide', name, bool(get_raw_server_side()))


def add_pfg_string_field_to_schema(schema, pfg_field, name):
    tl = zope.schema.TextLine()
    IEditableSchema(schema).addField(tl, name=name)
    setBaseFieldAttributes(schema, pfg_field, tl, name)
    setTaggedValue(schema, 'validators', name, [pfg_field.getRawFgStringValidator()])
    setSimpleAttributeFromAccessor(tl, pfg_field, 'default', 'getFgDefault')


def add_pfg_text_field_to_schema(schema, pfg_field, name):
    tl = zope.schema.Text()
    IEditableSchema(schema).addField(tl, name=name)
    setBaseFieldAttributes(schema, pfg_field, tl, name)
    setSimpleAttributeFromAccessor(tl, pfg_field, 'default', 'getFgDefault')


def add_pfg_int_field_to_schema(schema, pfg_field, name):
    tl = zope.schema.Int()
    IEditableSchema(schema).addField(tl, name=name)
    setBaseFieldAttributes(schema, pfg_field, tl, name)
    setIntAttributeFromAccessor(tl, pfg_field, 'default', 'getFgDefault')
    setIntAttributeFromAccessor(tl, pfg_field, 'min', 'getMinval')
    setIntAttributeFromAccessor(tl, pfg_field, 'max', 'getMaxval')


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
