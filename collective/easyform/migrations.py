from plone import api
from zope import schema
from plone.supermodel.exportimport import BaseHandler
from xml.etree.ElementTree import tostring
from Products.CMFPlone.utils import safe_unicode


# Get all the PFG forms present in the site.
# PFG_Forms = api.content.find(context=api.portal.get(), portal_type='FormFolder')


def migrate_pfg_content(pfg_form):
    """
    This will contain all the logic for migrating plone PFG forms content
    to easyform content.
    """

    # This will give us the list of String fields.
    fields = api.content.find(context=pfg_form, portal_type='FormStringField')
    final_content = ''
    for field in fields:
        string_obj = field.getObject()
        model_Schema_field = BaseHandler(string_obj)
        el = model_Schema_field.write(schema.Field, field.id, 'zope.schema.Field')
        final_content += tostring(el)
    return final_content


def migrate_pfg_string_field(pfg_string_field):
    tl = schema.TextLine()
    tl.title = safe_unicode(pfg_string_field.title)
    tl.description = safe_unicode(pfg_string_field.Description())
    tl.required = bool(pfg_string_field.getRequired())
    return tl
