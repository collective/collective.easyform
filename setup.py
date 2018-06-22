from setuptools import setup, find_packages

version = '2.0.0b6.dev0'

setup(
    name='collective.easyform',
    version=version,
    description='Forms for Plone',
    long_description=open('README.rst').read() +
    '\n' + open('CHANGES.rst').read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    ],
    keywords='form plone ttw builder email',
    author='Roman Kozlovskyi',
    author_email='krzroman@gmail.com',
    url='https://github.com/collective/collective.easyform',
    license='GPLv2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.api',
        'plone.app.dexterity',
        'plone.app.textfield >= 1.2.8',
        'plone.autoform',
        'plone.dexterity',
        'plone.namedfile',
        'plone.schema',
        'plone.schemaeditor >= 2.0.18',
        'plone.supermodel',
        'Products.CMFPlone',
        'Products.validation',
        # -*- Extra requirements: -*-
    ],
    extras_require={
        'recaptcha': [
            'plone.formwidget.recaptcha'
        ],
        'test': [
            'plone.app.testing[robot]',
            'plone.app.robotframework',
            'plone.app.contenttypes',
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
