# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = "3.0.5"

setup(
    name="collective.easyform",
    version=version,
    description="Forms for Plone",
    long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="form plone ttw builder email",
    author="Roman Kozlovskyi",
    author_email="krzroman@gmail.com",
    maintainer="Plone Release Team",
    maintainer_email="releaseteam@plone.org",
    url="https://github.com/collective/collective.easyform",
    license="GPLv2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "plone.api",
        "plone.app.dexterity",
        "plone.app.textfield >= 1.2.8",
        "plone.autoform",
        "plone.dexterity",
        "plone.namedfile",
        "plone.schema",
        "plone.schemaeditor >= 2.0.18",
        "plone.supermodel",
        "Products.CMFPlone",
        "Products.validation",
        "setuptools",
        "six",
        # -*- Extra requirements: -*-
    ],
    extras_require={
        "recaptcha": ["plone.formwidget.recaptcha"],
        "norobots": ["collective.z3cform.norobots"],
        "ploneformgen": ["Products.PloneFormGen",],
        "test": [
            "plone.app.testing[robot]",
            "plone.app.robotframework",
            "plone.app.contenttypes",
            "plone.formwidget.recaptcha",
            "robotframework-selenium2library",
            "robotframework-selenium2screenshots",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
