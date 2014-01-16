from collective.formulator.api import set_fields


def updateFields(obj, event):
    set_fields(obj.aq_parent, obj.schema)
