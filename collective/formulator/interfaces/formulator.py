from zope.interface import Interface
from zope import schema
from plone.directives import form
# -*- Additional Imports Here -*-


class IFormulator(form.Schema):
    """Forms for Plone"""

    # -*- schema definition goes here -*-
    form.omitted('schema')
    schema = schema.Object(
        title=u"Schema",
        schema=Interface,
    )
