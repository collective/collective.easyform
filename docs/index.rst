collective.easyform
===================

``collective.easyform`` is a form builder for Plone: editors create forms
through the web by adding fields, fieldsets and actions, without writing
code. Form input can be mailed, stored for download, handed to a custom
script, or held back until the sender confirmed their e-mail address.

EasyForm is a `Dexterity <https://github.com/plone/plone.dexterity>`_
content type; this documentation covers the 5.x releases for Plone 6.

The screenshots in this documentation are generated with
``docs/make_screenshots.py`` against a plain Plone 6 site - see the module
docstring if you want to regenerate them.

.. toctree::
   :maxdepth: 2

   adding
   fields
   actions


Contributing to the documentation
---------------------------------

The pages live in the ``docs`` directory of the repository and are built
with Sphinx. Every push and pull request runs the *Documentation* workflow
on GitHub (warnings are errors), and pull requests get a preview build on
Read the Docs - the link is posted as a comment on the pull request.

Further reading
---------------

* `Source code and issue tracker on GitHub
  <https://github.com/collective/collective.easyform>`_
* `Release notes <https://github.com/collective/collective.easyform/blob/master/CHANGES.rst>`_
* `collective.easyform on PyPI <https://pypi.org/project/collective.easyform/>`_
