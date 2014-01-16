from collective.formulator.api import set_actions


def updateActions(obj, event):
    set_actions(obj.aq_parent, obj.schema)
