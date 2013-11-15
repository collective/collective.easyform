from zope.interface import implements, Interface
from zope import schema as zs
from plone.directives import form
from plone.supermodel.interfaces import ISchema
# -*- Additional Imports Here -*-

class FormulatorSchema(ISchema):
    pass

class IFormulator(form.Schema):
    """Forms for Plone"""

    # -*- schema definition goes here -*-
    model = zs.Text(
        title=u"Model",
        default=u"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
    <schema>
    </schema>
</model>
""",
    )
