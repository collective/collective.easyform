import unittest
import six

from collective.easyform.tests.base import EasyFormFunctionalTestCase


class LikertFieldTests(unittest.TestCase):

    def _getTargetClass(self):
        from collective.easyform.fields import Likert
        return Likert

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        txt = self._makeOne()
        self.assertEqual(txt._type, six.text_type)

    def test_validate_not_required(self):
        field = self._makeOne(required=False)
        field.validate(None)
        field.validate(u'')

    def test_validate_with_answers(self):
        field = self._makeOne(required=False, questions=[u'Question 1'], answers=[u'Agree', u'Disagree'])
        field.validate(None)
        field.validate(u'')
        field.validate(u'1: Agree')
        self.assertRaises(ValueError, field.validate, u'1:agree')
        self.assertRaises(ValueError, field.validate, u'-1:agree')
        self.assertRaises(ValueError, field.validate, u'Agree')

    def test_validate_with_more_answers(self):
        field = self._makeOne(required=False, questions=[u'Question 1', u'Question 2'], answers=[u'Agree', u'Disagree'])
        field.validate(None)
        field.validate(u'')
        field.validate(u'1: Agree')
        field.validate(u'2: Agree')
        field.validate(u'1: Disagree, 2: Agree')
        self.assertRaises(ValueError, field.validate, u'1:agree')
        self.assertRaises(ValueError, field.validate, u'-1:agree')
        self.assertRaises(ValueError, field.validate, u'Agree')

    def test_parse(self):
        field = self._makeOne(required=False, questions=[u'Question 1', u'Question 2'], answers=[u'Agree', u'Disagree'])
        field.validate(None)
        self.assertEquals(dict(), field.parse(u''))
        self.assertEquals({1: u'Agree'}, field.parse(u'1: Agree'))
        self.assertEquals({2: u'Agree'}, field.parse(u'2: Agree'))
        self.assertEquals(
            {1: u'Disagree', 2: u'Agree'},
            field.parse(u'1: Disagree, 2: Agree')
        )


class LikerWidgetTests(EasyFormFunctionalTestCase):

    def setUp(self):
        super(LikerWidgetTests, self).setUp()
        ff1 = getattr(self.folder, "ff1")
        self.assertEqual(ff1.portal_type, u'EasyForm')

        from zope.interface import Interface
        from collective.easyform.api import set_fields
        from collective.easyform.api import set_actions
        from collective.easyform.actions import SaveData
        from collective.easyform.fields import Likert

        class IWithLikert(Interface):
            likert = Likert(questions=[u"Q1", u"Q2"], answers=[u"Agree", u"Disagree"])

        set_fields(ff1, IWithLikert)

        class IWithSaver(Interface):
            saver = SaveData(showFields=[])

        IWithSaver.setTaggedValue('context', ff1)
        set_actions(ff1, IWithSaver)
        import transaction
        transaction.commit()

    def test_widget_input(self):
        from zope.schema import getFieldsInOrder
        from collective.easyform.api import get_schema
        from collective.easyform.fields import Likert

        ff1 = getattr(self.folder, "ff1")
        schema = get_schema(ff1)
        fields = getFieldsInOrder(schema)
        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0][0], 'likert')
        self.assertTrue(isinstance(fields[0][1], Likert))

        # check that LikertWidget is used
        # and that questions and answers are rendered in a table
        view = ff1.restrictedTraverse('view')
        rendered = view()
        self.assertTrue(u"likert-widget" in rendered)
        self.assertTrue(u"<span>Q1</span>" in rendered)
        self.assertTrue(u"<span>Q2</span>" in rendered)
        self.assertTrue(u"<th>Agree</th>" in rendered)
        self.assertTrue(u"<th>Disagree</th>" in rendered)

    def test_likert_saved(self):
        import transaction
        ff1 = getattr(self.folder, "ff1")
        view = ff1.restrictedTraverse('view')
        # submit data to test value extraction from widget
        ff1.CSRFProtection = False  # no csrf protection
        view.request.form = {
            "form.buttons.submit": "Send",
            "form.widgets.likert.0": "Agree",
            "form.widgets.likert.1": "Disagree",
        }
        view.request.method = 'POST'
        rendered = view()
        self.assertTrue(u"Thank You" in rendered)
        self.assertTrue(u"1: Agree, 2: Disagree" in rendered)
        transaction.commit()
        actions_view = ff1.restrictedTraverse('actions')
        saver_view = actions_view.publishTraverse(actions_view.request, 'saver')
        data_view = saver_view.restrictedTraverse('@@data')
        rendered = data_view()
        from bs4 import BeautifulSoup
        radio_buttons = BeautifulSoup(rendered, 'html.parser').find_all(type="radio")
        self.assertEquals(len(radio_buttons), 4) # 2 rows of 2 answers

        # First question: answered Agree -> Agree input checked
        self.assertTrue("0_0" in radio_buttons[0]['id'])
        self.assertEquals(radio_buttons[0]['value'], "Agree")
        self.assertTrue(radio_buttons[0].has_attr('checked'))

        # First question: answered Agree -> Disagree input not checked
        self.assertTrue("0_1" in radio_buttons[1]['id'])
        self.assertEquals(radio_buttons[1]['value'], "Disagree")
        self.assertFalse(radio_buttons[1].has_attr('checked'))

        # Second question: answered Disagree -> Agree input not checked
        self.assertTrue("1_0" in radio_buttons[2]['id'])
        self.assertEquals(radio_buttons[2]['value'], "Agree")
        self.assertFalse(radio_buttons[2].has_attr('checked'))

        # Second question: answered Disagree -> Disagree input checked
        self.assertTrue("1_1" in radio_buttons[3]['id'])
        self.assertEquals(radio_buttons[3]['value'], "Disagree")
        self.assertTrue(radio_buttons[3].has_attr('checked'))
