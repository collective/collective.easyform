import logging

logger = logging.getLogger('collective.easyform.setuphandlers')


def uninstall(context):
    setup_tool = context.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-collective.easyform:uninstall')
