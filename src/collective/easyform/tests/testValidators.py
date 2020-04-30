# -*- coding: utf-8 -*-
try:
    from StringIO import StringIO  # for Python 2
except ImportError:
    from io import StringIO  # for Python 3
from collective.easyform import validators
from collective.easyform.api import get_schema
from collective.easyform.api import set_fields
from collective.easyform.browser.view import EasyFormForm
from collective.easyform.browser.view import ValidateFile
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.tests import base
from os.path import dirname
from os.path import join
from plone import api
from plone.formwidget.recaptcha.interfaces import IReCaptchaSettings
from plone.namedfile.file import NamedFile
from plone.namedfile.interfaces import INamed
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.RegistrationTool import EmailAddressInvalid
from Products.validation import validation
from z3c.form.interfaces import IFormLayer
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.interface import classImplements
from ZPublisher.BaseRequest import BaseRequest
from ZPublisher.HTTPRequest import FileUpload


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

    # Test value None and not required
    def test_basevalidator3(self):

        request = self.layer["request"]
        request.form["form.widgets.replyto"] = None

        fields = get_schema(self.ff1)

        fields["replyto"].required = False
        IFieldExtender(fields["replyto"]).validators = ["isEmail"]
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse("view")
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())

    # Test value None and required
    def test_basevalidator4(self):

        request = self.layer["request"]
        request.form["form.widgets.replyto"] = None

        fields = get_schema(self.ff1)

        IFieldExtender(fields["replyto"]).validators = ["isEmail"]
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


class LoadFixtureBase(base.EasyFormTestCase):
    """ test validator in form outside of fieldset

    The test methods are reused in TestFieldsetValidator.
    They use the same field, except that one has it in a fieldset.
    """

    schema_fixture = "single_field.xml"

    def afterSetUp(self):
        self.folder.invokeFactory("EasyForm", "ff1")
        self.ff1 = getattr(self.folder, "ff1")
        self.ff1.CSRFProtection = False  # no csrf protection
        self.ff1.showAll = True
        field_template = api.content.create(
            self.layer["portal"], "File", id="easyform_default_fields.xml"
        )
        with open(join(dirname(__file__), "fixtures", self.schema_fixture)) as f:
            filecontent = NamedFile(f.read(), contentType="application/xml")
        field_template.file = filecontent
        classImplements(BaseRequest, IFormLayer)
        validators.update_validators()

    def LoadRequestForm(self, **kwargs):
        request = self.layer["request"]
        request.form.clear()
        prefix = "form.widgets."
        for key in kwargs.keys():
            request.form[prefix + key] = kwargs[key]
        return request


class TestSingleFieldValidator(LoadFixtureBase):

    """ test validator in form outside of fieldset

    The test methods are reused in TestFieldsetValidator.
    They use the same field, except that one has it in a fieldset.
    """

    schema_fixture = "single_field.xml"

    def test_get_default(self):
        # With a GET, we should see the default value in the form.
        request = self.LoadRequestForm()
        request.method = "GET"
        form = EasyFormForm(self.ff1, request)()
        self.assertNotIn("Required input is missing.", form)
        self.assertIn('value="foo@example.org"', form)

    def test_required(self):
        data = {"replyto": ""}
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertIn("Required input is missing.", form)
        self.assertNotIn("Invalid email address.", form)

    def test_validator_in_fieldset(self):
        data = {
            "replyto": "bad email address",
        }
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertNotIn("Required input is missing.", form)
        self.assertIn("Invalid email address.", form)


class TestFieldsetValidator(TestSingleFieldValidator):

    """ test validator in fieldset

    This reuses the test methods from TestSingleFieldValidator.
    """

    schema_fixture = "fieldset_with_single_field.xml"


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
        self.assertEqual(v(None), None)
        self.assertRaises(EmailAddressInvalid, v, "@there.com")

    def test_isCommaSeparatedEmails(self):
        v = getUtility(IFieldValidator, name="isCommaSeparatedEmails")
        self.assertEqual(v("hi@there.com,another@two.com"), None)
        self.assertEqual(v("one@u.washington.edu,  two@u.washington.edu"), None)
        self.assertEqual(v(None), None)
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


class TestSingleRecaptchaValidator(LoadFixtureBase):

    """ Can't test captcha passes but we can test it fails
    """

    schema_fixture = "recaptcha.xml"

    def afterSetUp(self):
        super(TestSingleRecaptchaValidator, self).afterSetUp()

        # Put some dummy values for recaptcha
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReCaptchaSettings)
        proxy.public_key = u"foo"
        proxy.private_key = u"bar"

    def test_no_answer(self):
        data = {"verification": ""}
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertIn("The code you entered was wrong, please enter the new one.", form)
        self.assertNotIn("Thanks for your input.", form)

    def test_wrong(self):
        data = {"verification": "123"}
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertIn("The code you entered was wrong, please enter the new one.", form)
        self.assertNotIn("Thanks for your input.", form)


class TestFieldsetRecaptchaValidator(TestSingleRecaptchaValidator):
    """ make sure it works inside a fieldset too
    """

    schema_fixture = "fieldset_recaptcha.xml"


class DummyUpload(FileUpload):
    def __init__(self, size, filename):
        self.file = StringIO("x" * size)
        self.file.filename = filename
        self.file.headers = []
        self.file.name = "file1"
        self.file.file = self.file
        FileUpload.__init__(self, self.file)


class TestFieldsetFileValidator(LoadFixtureBase):
    """ ensure file validators works
    """

    schema_fixture = "fieldset_file.xml"

    def test_wrong_type(self):
        data = {"file1": DummyUpload(20, "blah.txt")}
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertNotIn("Thanks for your input.", form)
        self.assertIn('File type "TXT" is not allowed!', form)

    def test_right_type(self):
        data = {"file1": DummyUpload(20, "blah.pdf")}
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertIn("Thanks for your input.", form)

    def test_too_big(self):
        data = {"file1": DummyUpload(2000, "blah.pdf")}
        request = self.LoadRequestForm(**data)
        request.method = "POST"
        form = EasyFormForm(self.ff1, request)()
        self.assertNotIn("Thanks for your input.", form)
        self.assertIn("File is bigger than allowed size of 300 bytes!", form)
