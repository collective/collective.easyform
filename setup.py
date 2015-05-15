from setuptools import setup, find_packages
import os

version = '1.0a2'

setup(name='collective.easyform',
      version=version,
      description="Forms for Plone",
      long_description=open("README.rst").read() +
      "\n" + open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='form plone ttw',
      author='Roman Kozlovskyi',
      author_email='krzroman@gmail.com',
      url='https://github.com/quintagroup/collective.easyform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.textfield',
          'plone.dexterity',
          'plone.directives.form',
          'plone.namedfile',
          'plone.schemaeditor',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'recaptcha': [
              'plone.formwidget.recaptcha'
          ],
          'test': [
              'plone.app.testing[robot]',
              'plone.app.robotframework',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
