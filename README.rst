=====================================
EasyForm - Form Builder for CMS Plone
=====================================

.. image:: https://badge.fury.io/py/collective.easyform.svg
    :target: https://badge.fury.io/py/collective.easyform
    :alt: latest release version badge by Badge Fury

.. image:: https://travis-ci.org/collective/collective.easyform.png?branch=master
    :target: https://travis-ci.org/collective/collective.easyform
    :alt: Travis CI status

.. image:: https://coveralls.io/repos/github/collective/collective.easyform/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/collective.easyform?branch=master
    :alt: Coveralls status

The add on ``collective.easyform`` adds Plone content types for form creation.

EasyForm provides a Plone form builder through-the-web using fields, widgets, actions and validators (based on Dexterity).
Form input can be saved or emailed.
A simple and user-friendly interface allows non-programmers to create custom forms.

Note: This Plone package is similar to Archetypes based ``Products.PloneFormGen`` for Plone versions 1 to 4.
Dexterity is a new platform for content types in Plone and will be used instead of Archetypes in Plone 5.


Usage
-----

- Install product (in your buildout.cfg add ‘collective.easyform’ to the eggs section),
  rerun your Plone instance and activate ``EasyForm``.
- Choose EasyForm from the toolbars 'Add new' menu.
  Insert form title, description and other settings.
- Add fields or fieldsets to create a unique form that will meet your particular requirements.
  There are enough basic field types to satisfy any demands:

  - File Upload,
  - Text line (String),
  - Integer,
  - Yes/No,
  - Date, Date/Time,
  - Floating-point number,
  - Choice,
  - Rich Text,
  - Image,
  - Multiple Choice,
  - Text,
  - Password,
  - ReСaptcha.
- Continue to customize form by setting the order of fields,
  defining required and hidden ones,
  choosing validator, if necessary,
  and other field type specific settings.

See quick overview of this product:

.. image:: http://quintagroup.com/services/plone-development/products/easyform/easyform-youtube.png
    :target: https://www.youtube.com/watch?v=DMCYnYE9RKU
    :alt: EasyForm instructional video


Source Code and Contributions
-----------------------------

If you want to help with the development (improvement, update, bug-fixing, ...) of ``collective.easyform`` this is a great idea!

- `Source code at Github <https://github.com/collective/collective.easyform>`_
- `Issue tracker at Github <https://github.com/collective/collective.easyform/issues>`_

You can clone it or `get access to the github-collective <http://collective.github.com/>`_ and work directly on the project.
Please do larger changes on a branch and submit a Pull Request.

Maintainer of collective.easyform is the Plone Collective community.

We appreciate any contribution and if a release is needed to be done on pypi,
please just contact one of the owners or maintainers mentioned at the Python Package Index page

Contribute
----------

.. figure:: http://collective.com/services/plone-development/products/easyform/easyform.png
    :target: https://github.com/collective/collective.easyform
    :alt: Logo

- Issue Tracker: https://github.com/collective/collective.easyform/issues
- Source Code: https://github.com/collective/collective.easyform


License
-------

The project is licensed under the GPLv2.


Compatibility
-------------

- 2.x targets Plone 5.x
- 1.x targets Plone 4.x
