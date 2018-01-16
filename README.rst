=================================
EasyForm - Form Builder for Plone
=================================

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

EasyForm provides a Plone form builder through-the-web using fields, widgets, actions and validators (based on `Dexterity <https://github.com/plone/plone.dexterity>`_).

Form input can be saved or emailed.
A simple and user-friendly interface allows non-programmers to create custom forms.

**Note:** This Plone package is similar to `Archetypes <http://docs.plone.org/develop/plone/content/archetypes/>`_ based `Products.PloneFormGen <https://github.com/smcmahon/Products.PloneFormGen>`_ for Plone versions 1 to 4.

Dexterity is the default framework for building content types in Plone 5.

Installation
============

Install collective.easyform by adding it to your buildout:

.. code-block:: shell

    [buildout]

    ...

    eggs =
        collective.easyform


Run buildout:

.. code-block:: shell

    bin/buildout

The last step is to activate ``EasyForm`` in the Control Panel.

Usage
=====

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

Click on the picture below for a short introduction video:

.. image:: http://quintagroup.com/services/plone-development/products/easyform/easyform-youtube.png
    :target: https://www.youtube.com/watch?v=DMCYnYE9RKU
    :alt: EasyForm instructional video


ReCaptcha support
=================

Install ``collective.easyform`` with the  ``recaptcha`` extra:

.. code-block:: shell

    [buildout]

    ...

    eggs =
        collective.easyform [recaptcha]


And run buildout and install EasyForm as described above.

Then go to the EasyFrom controlpanel (``/@@easyform-controlpanel``) and add the "ReCaptcha" field to "Allowed Fields".
Alternatively, activate it by adding it as an ``registry.xml`` entry for Generic Setup:

.. code-block:: xml

    <record name="easyform.allowedFields">
      <value purge="False">
        <element>collective.easyform.fields.ReCaptcha</element>
      </value>
    </record>

Then add the ReCaptcha field to the forms where you want to use it.
As field type use ``ReCaptcha`` and set ``require`` to false.

As last step you might want to not include the recaptcha field in the thanks page and mailer action.
To do that, edit the form, go to the "Thanks page" settings, disable "Show all fields" and then include only those you want.
Likewise for the mailing: Open the form actions via the actions toolbar menu and edit the mailer settings accordingly.

Actions
=======

You can choose between the following actions after form submission:

 * Mailer
 * DataStorage
 * CustomScript

The mailer stores a HTML template for sending the results of the form. You can override it with a file named
`easyform_mail_body_default.pt` in your site. If it is not found the default from the `default_schemata` directory
of this package is taken. If you plan to override start with the the `mail_body_default.pt` file and make sure
it is a valid pagetemplate.


Source Code and Contributions
=============================

If you want to help with the development (improvement, update, bug-fixing, ...) of ``collective.easyform`` this is a great idea!

- `Source code at Github <https://github.com/collective/collective.easyform>`_
- `Issue tracker at Github <https://github.com/collective/collective.easyform/issues>`_

You can clone it or `get access to the github-collective <https://github.com/collective>`_ and work directly on the project.

Please do larger changes on a branch and submit a Pull Request.

Maintainer of ``collective.easyform`` is the Plone Collective community.

We appreciate any contribution !

For new release, please contact one of the owners or maintainers mentioned at the `Python Package Index page <https://pypi.python.org/pypi/collective.easyform>`_.

Contribute
==========

- Issue Tracker: https://github.com/collective/collective.easyform/issues
- Source Code: https://github.com/collective/collective.easyform


License
=======

The project is licensed under the GPLv2.


Compatibility
=============

- 1.x targets Plone 4.x
- 2.x targets Plone 5.x onwards

