# -*- coding: utf-8 -*-
from collective.easyform.tests import base
from os import getenv
from os import listdir
from os import path
from plone.testing import layered
from robotsuite import RobotTestSuite
from unittest import TestSuite


RUN_ROBOT_TESTS_ENV = "RUN_ROBOT_TESTS"
try:
    RUN_ROBOT_TESTS = int(getenv(RUN_ROBOT_TESTS_ENV, 0))
except (ValueError, TypeError, AttributeError):
    print("Ignored non-integer {0} environment variable.".format(RUN_ROBOT_TESTS_ENV))
    RUN_ROBOT_TESTS = False


def test_suite():
    suite = TestSuite()
    if not RUN_ROBOT_TESTS:
        print(
            "WARNING: Ignoring robot tests because {0} environment variable is not set.".format(
                RUN_ROBOT_TESTS_ENV
            )
        )
        print(
            "Half of the robot tests would fail because modals are not working. Fixing the modals would be appreciated."
        )
        return suite
    current_dir = path.abspath(path.dirname(__file__))
    robot_dir = path.join(current_dir, "robot")
    robot_tests = [
        path.join("robot", doc)
        for doc in listdir(robot_dir)
        if doc.startswith("test") and doc.endswith(".robot")
    ]
    for test in robot_tests:
        suite.addTests([layered(RobotTestSuite(test), layer=base.ROBOT_TESTING)])
    return suite
