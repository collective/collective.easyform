# -*- coding: utf-8 -*-
from collective.easyform.tests import base
from os import listdir
from os import path
from plone.testing import layered
from robotsuite import RobotTestSuite
from unittest import TestSuite


def test_suite():
    suite = TestSuite()
    current_dir = path.abspath(path.dirname(__file__))
    robot_dir = path.join(current_dir, 'robot')
    robot_tests = [
        path.join('robot', doc)
        for doc in listdir(robot_dir)
        if doc.startswith('test') and doc.endswith('.robot')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(
                RobotTestSuite(test),
                layer=base.ROBOT_TESTING
            ),
        ])
    suite.level = 3
    return suite
