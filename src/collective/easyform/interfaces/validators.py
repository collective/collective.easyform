# -*- coding: utf-8 -*-
from Products.PageTemplates.Expressions import getEngine
from zope.tales import tales

import re
import zope.schema.interfaces


class InvalidTALESError(zope.schema.ValidationError):
    __doc__ = u"Please enter a valid TALES expression."


def isTALES(value):
    if value.strip():
        try:
            getEngine().compile(value)
        except tales.CompilerError:
            raise InvalidTALESError
    return True


class InvalidCSSClassNameError(zope.schema.ValidationError):
    __doc__ = u"Please enter valid CSS class names."


def cssClassConstraint(value):
    if not value:
        # Let the system for required take care of None values
        return True
    parts = value.strip().split(" ")
    for part in parts:
        if not re.match(r'^[A-Za-z]*[A-Za-z\-\_0-9]*[\w][\s]?$', part):
            raise InvalidCSSClassNameError
    return True

