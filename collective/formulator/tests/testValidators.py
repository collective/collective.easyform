#
# Test PloneFormGen initialisation and set-up
#

from zope.interface import classImplements
from z3c.form.interfaces import IFormLayer
from ZPublisher.BaseRequest import BaseRequest
from collective.formulator.tests import pfgtc
from collective.formulator.api import get_fields, set_fields
from collective.formulator.interfaces import IFieldExtender

#from collective.formulator.content import validationMessages
from Products.validation import validation

FORM_DATA = {
    'topic': u'test subject',
    'replyto': u'test@test.org',
    'comments': u'test comments',
}


class TestBaseValidators(pfgtc.PloneFormGenTestCase):

    """ test base validators """

    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)
        self.folder.invokeFactory('Formulator', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.checkAuthenticator = False  # no csrf protection
        classImplements(BaseRequest, IFormLayer)

        request = self.app.REQUEST
        for i in FORM_DATA:
            request.form['form.widgets.%s' % i] = FORM_DATA[i]

    def test_defaultvalidator(self):
        view = self.ff1.restrictedTraverse('view')
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())
        self.assertEqual(data, FORM_DATA)

    def test_basevalidator(self):
        fields = get_fields(self.ff1)
        IFieldExtender(fields['replyto']).validators = ["isEmail"]
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse('view')
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())
        self.assertEqual(data, FORM_DATA)

    def test_basevalidator2(self):
        fields = get_fields(self.ff1)
        IFieldExtender(fields['comments']).validators = ["isInt", "isURL"]
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse('view')
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)

    def test_talvalidator(self):
        fields = get_fields(self.ff1)
        IFieldExtender(
            fields['comments']).TValidator = "python: value == 'comments'"
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse('view')
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(errors, ())
        self.assertEqual(data, FORM_DATA)

    def test_talvalidator2(self):
        fields = get_fields(self.ff1)
        IFieldExtender(fields['comments']).TValidator = "python: !value"
        set_fields(self.ff1, fields)
        view = self.ff1.restrictedTraverse('view')
        form = view.form_instance
        form.update()

        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)


class TestCustomValidators(pfgtc.PloneFormGenTestCase):

    """ test our validators """

    def test_inExNumericRange(self):
        v = validation.validatorFor('inExNumericRange')
        self.assertEqual(v(10, minval=1, maxval=20), 1)
        self.assertEqual(v('10', minval=1, maxval=20), 1)
        self.assertEqual(v('1', minval=1, maxval=20), 1)
        self.assertEqual(v('20', minval=1, maxval=20), 1)
        self.assertNotEqual(v(0, minval=1, maxval=5), 1)
        self.assertNotEqual(v(6, minval=1, maxval=5), 1)
        self.assertNotEqual(v(4, minval=5, maxval=3), 1)

    def test_isNotTooLong(self):
        v = validation.validatorFor('isNotTooLong')
        self.assertEqual(v('', maxlength=20), 1)
        self.assertEqual(v('1234567890', maxlength=20), 1)
        self.assertEqual(v('1234567890', maxlength=10), 1)
        self.assertEqual(v('1234567890', maxlength=0), 1)
        self.assertNotEqual(v('1234567890', maxlength=9), 1)
        self.assertNotEqual(v('1234567890', maxlength=1), 1)

    def test_isChecked(self):
        v = validation.validatorFor('isChecked')
        self.assertEqual(v('1'), 1)
        self.assertNotEqual(v('0'), 1)

    def test_isUnchecked(self):
        v = validation.validatorFor('isUnchecked')
        self.assertEqual(v('0'), 1)
        self.assertNotEqual(v('1'), 1)

    def test_isNotLinkSpam(self):
        v = validation.validatorFor('isNotLinkSpam')
        good = """I am link free and proud of it"""
        bad1 = """<a href="mylink">Bad.</a>"""
        bad2 = """http://bad.com"""
        bad3 = """www.Bad.com"""
        bad = (bad1, bad2, bad3)

        class Mock(object):
            validate_no_link_spam = 1
        mock = Mock()
        kw = {'field': mock}
        self.assertEqual(v(good, **kw), 1)
        for b in bad:
            self.assertNotEqual(v(b, **kw), 1,
                                '"%s" should be considered a link.' % b)

    def test_isNotTooLong2(self):
        v = validation.validatorFor('isNotTooLong')
        v.maxlength = 10
        self.assertEqual(v('abc'), 1)
        self.assertNotEqual(v('abcdefghijklmnopqrstuvwxyz'), 1)

        # there was a bug where widget.maxlength could possibly be defined as
        # '' which means calling int(widget.maxlength) would fail

        class Mock(object):
            pass
        field = Mock()
        field.widget = Mock()
        field.widget.maxlength = ''

        self.assertEqual(v('abc', field=field), 1)

    def test_isEmail(self):
        v = validation.validatorFor('isEmail')
        self.assertEqual(v('hi@there.com'), 1)
        self.assertEqual(v('one@u.washington.edu'), 1)
        self.assertNotEqual(v('@there.com'), 1)

    def test_isCommaSeparatedEmails(self):
        v = validation.validatorFor('pfgv_isCommaSeparatedEmails')
        self.assertEqual(v('hi@there.com,another@two.com'), 1)
        self.assertEqual(
            v('one@u.washington.edu,  two@u.washington.edu'), 1)
        self.assertNotEqual(v('abc@plone.org; xyz@plone.org'), 1)


class TestCustomValidatorMessages(pfgtc.PloneFormGenTestCase):

    """ Test friendlier validation framework """

    def test_messageMassage(self):

        # s = "Validation failed(isUnixLikeName): something is not a valid identifier."
        # self.assertEqual(validationMessages.cleanupMessage(s, self, self), u'pfg_isUnixLikeName')

        #s = "Something is required, please correct."
        # self.assertEqual(
            # validationMessages.cleanupMessage(s, self, self),
            # u'pfg_isRequired')

        #s = "Validation failed(isNotTooLong): 'something' is too long. Must be no longer than some characters."
        #response = validationMessages.cleanupMessage(s, self, self)
        #self.assertEqual(response, u'pfg_too_long')
        pass

    def test_stringValidators(self):
        """ Test string validation
        """

        from Products.validation.exceptions import UnknowValidatorError
        from Products.validation import validation as v

        self.assertRaises(
            UnknowValidatorError, v.validate, 'noValidator', 'test')

        self.assertNotEqual(v.validate('pfgv_isEmail', 'test'), 1)

        self.assertEqual(v.validate('pfgv_isEmail', 'test@test.com'), 1)

        self.assertEqual(v.validate('pfgv_isZipCode', '12345'), 1)
        self.assertEqual(v.validate('pfgv_isZipCode', '12345-1234'), 1)
        # Canadian zip codes
        self.assertEqual(v.validate('pfgv_isZipCode', 'T2X 1V4'), 1)
        self.assertEqual(v.validate('pfgv_isZipCode', 'T2X1V4'), 1)
        self.assertEqual(v.validate('pfgv_isZipCode', 't2x 1v4'), 1)


# if __name__ == '__main__':
    # framework()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBaseValidators))
    # suite.addTest(makeSuite(TestCustomValidators))
    # suite.addTest(makeSuite(TestCustomValidatorMessages))
    return suite
