from setuptools import setup, find_packages

version = '1.0.1'

setup(name='collective.easyform',
      version=version,
      description="Forms for Plone",
      long_description=open("README.rst").read() +
      "\n" + open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='form plone ttw',
      author='Roman Kozlovskyi',
      author_email='krzroman@gmail.com',
      maintainer='Plone Release Team',
      maintainer_email='releaseteam@plone.org',
      url='https://github.com/collective/collective.easyform',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.textfield',
          'plone.autoform',
          'plone.dexterity',
          'plone.namedfile',
          'plone.schemaeditor==2.0.7',
          'plone.supermodel',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'recaptcha': [
              'plone.formwidget.recaptcha'
          ],
          'test': [
              'plone.app.contenttypes',
              'plone.app.testing[robot]',
              'plone.app.robotframework',
              'plone.restapi',
              'plone.api',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
