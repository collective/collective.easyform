import unittest

from collective.easyform.tests.base import EasyFormFunctionalTestCase
from zope.schema.interfaces import RequiredMissing


class LikertFieldTests(unittest.TestCase):

    def _getTargetClass(self):
        from collective.easyform.fields import Likert
        return Likert

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        txt = self._makeOne()
        self.assertEqual(txt._type, str)

    def test_validate_not_required(self):
        field = self._makeOne(required=False)
        field.validate(None)
        field.validate('')

    def test_validate_with_answers(self):
        field = self._makeOne(required=False, questions=['Question 1'], answers=['Agree', 'Disagree'])
        field.validate(None)
        field.validate('')
        field.validate('1: Agree')
        self.assertRaises(ValueError, field.validate, '1:agree')
        self.assertRaises(ValueError, field.validate, '-1:agree')
        self.assertRaises(ValueError, field.validate, 'Agree')

    def test_validate_with_more_answers(self):
        field = self._makeOne(required=False, questions=['Question 1', 'Question 2'], answers=['Agree', 'Disagree'])
        field.validate(None)
        field.validate('')
        field.validate('1: Agree')
        field.validate('2: Agree')
        field.validate('1: Disagree, 2: Agree')
        self.assertRaises(ValueError, field.validate, '1:agree')
        self.assertRaises(ValueError, field.validate, '-1:agree')
        self.assertRaises(ValueError, field.validate, 'Agree')

    def test_validate_required(self):
        from collective.easyform.fields import AllAnswersRequired

        field = self._makeOne(required=True, questions=['Question 1', 'Question 2'], answers=['Agree', 'Disagree'])

        field.validate('1: Disagree, 2: Agree')
        self.assertRaises(RequiredMissing, field.validate, None)
        self.assertRaises(AllAnswersRequired, field.validate, '1:Agree')
        self.assertRaises(AllAnswersRequired, field.validate, '')

    def test_parse(self):
        field = self._makeOne(required=False, questions=['Question 1', 'Question 2'], answers=['Agree', 'Disagree'])
        field.validate(None)
        self.assertEqual(dict(), field.parse(''))
        self.assertEqual({1: 'Agree'}, field.parse('1: Agree'))
        self.assertEqual({2: 'Agree'}, field.parse('2: Agree'))
        self.assertEqual(
            {1: 'Disagree', 2: 'Agree'},
            field.parse('1: Disagree, 2: Agree')
        )


class LikerWidgetTests(EasyFormFunctionalTestCase):

    def setUp(self):
        super().setUp()
        ff1 = getattr(self.folder, "ff1")
        self.assertEqual(ff1.portal_type, 'EasyForm')

        from zope.interface import Interface
        from collective.easyform.api import set_fields
        from collective.easyform.api import set_actions
        from collective.easyform.actions import SaveData
        from collective.easyform.fields import Likert

        class IWithLikert(Interface):
            likert = Likert(questions=["Q1", "Q2"], answers=["Agree", "Disagree"])

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
        self.assertTrue("likert-widget" in rendered)
        self.assertTrue("<span>Q1</span>" in rendered)
        self.assertTrue("<span>Q2</span>" in rendered)
        self.assertTrue("Agree</th>" in rendered)
        self.assertTrue("Disagree</th>" in rendered)

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
        self.assertTrue("Thank You" in rendered)
        self.assertTrue("1: Agree, 2: Disagree" in rendered)
        transaction.commit()
        actions_view = ff1.restrictedTraverse('actions')
        saver_view = actions_view.publishTraverse(actions_view.request, 'saver')
        data_view = saver_view.restrictedTraverse('@@data')
        rendered = data_view()
        from bs4 import BeautifulSoup
        radio_buttons = BeautifulSoup(rendered, 'html.parser').find_all(type="radio")
        self.assertEqual(len(radio_buttons), 4) # 2 rows of 2 answers

        # First question: answered Agree -> Agree input checked
        self.assertTrue("0_0" in radio_buttons[0]['id'])
        self.assertEqual(radio_buttons[0]['value'], "Agree")
        self.assertTrue(radio_buttons[0].has_attr('checked'))

        # First question: answered Agree -> Disagree input not checked
        self.assertTrue("0_1" in radio_buttons[1]['id'])
        self.assertEqual(radio_buttons[1]['value'], "Disagree")
        self.assertFalse(radio_buttons[1].has_attr('checked'))

        # Second question: answered Disagree -> Agree input not checked
        self.assertTrue("1_0" in radio_buttons[2]['id'])
        self.assertEqual(radio_buttons[2]['value'], "Agree")
        self.assertFalse(radio_buttons[2].has_attr('checked'))

        # Second question: answered Disagree -> Disagree input checked
        self.assertTrue("1_1" in radio_buttons[3]['id'])
        self.assertEqual(radio_buttons[3]['value'], "Disagree")
        self.assertTrue(radio_buttons[3].has_attr('checked'))
