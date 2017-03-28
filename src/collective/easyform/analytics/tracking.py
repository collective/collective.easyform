# -*- coding: utf-8 -*-
from collective.easyform.interfaces import IEasyForm
from collective.googleanalytics.tracking import AnalyticsBaseTrackingPlugin
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class FormAnalyticsPlugin(AnalyticsBaseTrackingPlugin):
    """
    A tracking plugin to track form views, submissions and errors.
    """

    __call__ = ViewPageTemplateFile('tracking.pt')

    def form_status(self):
        """
        Returns the status of the form, which can be None (not a form),
        'form' (viewing the form), 'thank-you' (form succesfully submitted),
        or 'error' (form has validation errors).
        """

        if not IEasyForm.providedBy(self.context):
            return None

#         if 'form_submit' in self.request.form.keys():
#             result = 'error'
#         elif IEasyForm.providedBy(self.context):
#             result = 'thank-you'
#         else:
#             result = 'form'
#         return result
