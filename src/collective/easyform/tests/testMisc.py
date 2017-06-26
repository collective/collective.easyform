# -*- coding: utf-8 -*-
#
# Integration tests for miscellaneous stuff
#

from collective.easyform.actions import OrderedDict
from collective.easyform.tests import base


class TestMisc(base.EasyFormTestCase):
    ''' test miscellaneous stuff '''

    def test_ordereddict_reverse(self):
        d = OrderedDict()
        d['a'] = 1
        d['b'] = 2
        d['c'] = 3
        self.assertEqual(
            d.reverse(),
            [('c', 3), ('b', 2), ('a', 1)]
        )
