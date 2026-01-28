from .actions import IAction
from collective.easyform import config
from collective.easyform import easyformMessageFactory as _
from plone.autoform import directives

import zope.interface
import zope.schema.interfaces


MODIFY_PORTAL_CONTENT = "cmf.ModifyPortalContent"


class ICustomScript(IAction):
    """Executes a Python script for form data."""

    directives.read_permission(ProxyRole=MODIFY_PORTAL_CONTENT)
    directives.write_permission(ProxyRole=config.EDIT_PYTHON_PERMISSION)
    ProxyRole = zope.schema.Choice(
        title=_("label_script_proxy", default="Proxy role"),
        description=_(
            "help_script_proxy", default="Role under which to run the script."
        ),
        default="none",
        required=True,
        vocabulary="easyform.ProxyRoleChoices",
    )
    directives.read_permission(ScriptBody=MODIFY_PORTAL_CONTENT)
    directives.write_permission(ScriptBody=config.EDIT_PYTHON_PERMISSION)
    ScriptBody = zope.schema.Text(
        title=_("label_script_body", default="Script body"),
        description=_("help_script_body", default="Write your script here."),
        default=config.DEFAULT_SCRIPT,
        required=False,
        missing_value="",
    )
