# -*- coding: utf-8 -*-
from collective.easyform import validators
from collective.easyform.api import get_schema
from collective.easyform.api import set_fields
from collective.easyform.browser.view import ValidateFile
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.tests import base
from plone.namedfile.interfaces import INamed
from Products.CMFPlone.RegistrationTool import EmailAddressInvalid
from Products.validation import validation
from z3c.form.interfaces import IFormLayer
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.interface import classImplements
from ZPublisher.BaseRequest import BaseRequest


IFieldValidator = validators.IFieldValidator

FORM_DATA = {
    "topic": u"test subject",
    "replyto": u"test@test.org",
    "comments": u"test comments",
}


class TestBaseValidators(base.EasyFormTestCase):

    """ test base validators """

    def afterSetUp(self):
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.ff1.CSRFProtection = False  # no csrf protection
        classImplements(BaseRequest, IFormLayer)
        validators.update_validators()

        request = self.layer["request"]
        for i in FORM_DATA:
            request.form["form.widgets.{0}".format(i)] = FORM_DATA[i]

    def test_defaultvalidator(self):
        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())
        self.assertEqual(data, FORM_DATA)

    def test_basevalidator(self):
        fields = get_schema(self.ff1)
        IFieldExtender(fields["replyto"]).validators = ["isEmail"]
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())
        self.assertEqual(data, FORM_DATA)

    def test_basevalidator2(self):
        fields = get_schema(self.ff1)
        IFieldExtender(fields["comments"]).validators = ["isInt", "isURL"]
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)

    def test_talvalidator(self):
        fields = get_schema(self.ff1)
        IFieldExtender(fields["comments"]).TValidator = "python: value == 'comments'"
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())
        self.assertEqual(data, FORM_DATA)

    def test_talvalidator2(self):
        fields = get_schema(self.ff1)
        IFieldExtender(fields["comments"]).TValidator = "python: !value"
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)


class TestCustomValidators(base.EasyFormTestCase):

    """ test our validators """

    def ttest_inExNumericRange(self):
        v = validation.validatorFor("inExNumericRange")
        self.assertEqual(v(10, minval=1, maxval=20), 1)
        self.assertEqual(v("10", minval=1, maxval=20), 1)
        self.assertEqual(v("1", minval=1, maxval=20), 1)
        self.assertEqual(v("20", minval=1, maxval=20), 1)
        self.assertNotEqual(v(0, minval=1, maxval=5), 1)
        self.assertNotEqual(v(6, minval=1, maxval=5), 1)
        self.assertNotEqual(v(4, minval=5, maxval=3), 1)

    def ttest_isNotTooLong(self):
        v = validation.validatorFor("isNotTooLong")
        self.assertEqual(v("", maxlength=20), 1)
        self.assertEqual(v("1234567890", maxlength=20), 1)
        self.assertEqual(v("1234567890", maxlength=10), 1)
        self.assertEqual(v("1234567890", maxlength=0), 1)
        self.assertNotEqual(v("1234567890", maxlength=9), 1)
        self.assertNotEqual(v("1234567890", maxlength=1), 1)

    def test_isChecked(self):
        v = getUtility(IFieldValidator, name="isChecked")
        self.assertEqual(v("1"), None)
        self.assertNotEqual(v("0"), None)

    def test_isUnchecked(self):
        v = getUtility(IFieldValidator, name="isUnchecked")
        self.assertEqual(v("0"), None)
        self.assertNotEqual(v("1"), None)

    def test_isNotLinkSpam(self):
        v = getUtility(IFieldValidator, name="isNotLinkSpam")
        good = """I am link free and proud of it"""
        bad1 = """<a href="mylink">Bad.</a>"""
        bad2 = """http://bad.com"""
        bad3 = """www.Bad.com"""
        bad = (bad1, bad2, bad3)

        self.assertEqual(v(good), None)
        for b in bad:
            self.assertNotEqual(
                v(b), None, '"{0}" should be considered a link.'.format(b)
            )

    def ttest_isNotTooLong2(self):
        v = validation.validatorFor("isNotTooLong")
        v.maxlength = 10
        self.assertEqual(v("abc"), 1)
        self.assertNotEqual(v("abcdefghijklmnopqrstuvwxyz"), 1)

        # there was a bug where widget.maxlength could possibly be defined as
        # '' which means calling int(widget.maxlength) would fail

        class Mock(object):
            pass

        field = Mock()
        field.widget = Mock()
        field.widget.maxlength = ""

        self.assertEqual(v("abc", field=field), 1)

    def test_isEmail(self):
        v = getUtility(IFieldValidator, name="isValidEmail")
        self.assertEqual(v("hi@there.com"), None)
        self.assertEqual(v("one@u.washington.edu"), None)
        self.assertRaises(EmailAddressInvalid, v, "@there.com")

    def test_isCommaSeparatedEmails(self):
        v = getUtility(IFieldValidator, name="isCommaSeparatedEmails")
        self.assertEqual(v("hi@there.com,another@two.com"), None)
        self.assertEqual(v("one@u.washington.edu,  two@u.washington.edu"), None)
        self.assertNotEqual(v("abc@plone.org; xyz@plone.org"), None)


class TestCustomValidatorMessages(base.EasyFormTestCase):
    """ Test friendlier validation framework """

    def test_stringValidators(self):
        """ Test string validation
        """
        validators.update_validators()

        def validator(n):
            return getUtility(IFieldValidator, name=n)

        def validate(n, v):
            return validator(n) and validator(n)(v)

        self.assertRaises(ComponentLookupError, validate, "noValidator", "test")

        self.assertNotEqual(validate("isEmail", "test"), None)

        self.assertEqual(validate("isEmail", "test@test.com"), None)

        self.assertEqual(validate("isZipCode", "12345"), None)
        self.assertNotEqual(validate("isZipCode", "12345-1234"), None)


class DummyFile(object):
    def __init__(self, size=1, filename=""):
        self.size = size
        self.filename = filename

    def getSize(self):
        return self.size


classImplements(DummyFile, INamed)


class TestSizeValidator(base.EasyFormTestCase):
    def afterSetUp(self):
        self.request = self.layer["request"]
        self.validate_view = ValidateFile(self.portal, self.request)

    def test_filesize_none_validation(self):
        self.assertFalse(self.validate_view(None))

    def test_filesize_no_file_validation(self):
        self.assertFalse(self.validate_view("not a file"))

    def test_filiesize_smallsize_validation(self):
        self.assertFalse(self.validate_view(DummyFile(1024)))

    def test_filiesize_bigsize_validation(self):
        self.assertEqual(
            translate(self.validate_view(DummyFile(1000000000))),
            u"File is bigger than allowed size of 1048576 bytes!",
        )

    def test_filiesize_bigsize_custom_validation(self):
        self.assertEqual(
            translate(self.validate_view(DummyFile(1025), 1024)),
            u"File is bigger than allowed size of 1024 bytes!",
        )

    def test_forbidden_type_validation_fail(self):
        validation = self.validate_view(
            DummyFile(filename="foo.ZIP"), forbidden_types=("zip",)
        )
        self.assertEqual(translate(validation), u'File type "ZIP" is not allowed!')

    def test_forbidden_type_validation_pass(self):
        validation = self.validate_view(
            DummyFile(filename="foo.txt"), forbidden_types=("zip",)
        )
        self.assertFalse(validation)

    def test_allowed_type_validation_fail(self):
        validation = self.validate_view(
            DummyFile(filename="foo.ZIP"), allowed_types=("txt",)
        )
        self.assertEqual(translate(validation), u'File type "ZIP" is not allowed!')

    def test_allowed_type_validation_pass(self):
        validation = self.validate_view(
            DummyFile(filename="foo.txt"), allowed_types=("txt",)
        )
        self.assertFalse(validation)

    def test_allowed_type_no_ext(self):
        validation = self.validate_view(
            DummyFile(filename="foo"), allowed_types=("txt",)
        )
        self.assertEqual(translate(validation), u'File type "" is not allowed!')
