# -*- coding: utf-8 -*-

import os
import unittest

from plone.testing import layered

from collective.easyform.tests import base

import robotsuite


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc)
        for doc in os.listdir(robot_dir)
        if doc.startswith('test') and doc.endswith('.robot')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(
                robotsuite.RobotTestSuite(test),
                layer=base.ROBOT_TESTING
            ),
        ])
    return suite
