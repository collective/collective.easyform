Introduction
============

.. image:: https://travis-ci.org/quintagroup/collective.easyform.png?branch=master
    :target: https://travis-ci.org/quintagroup/collective.easyform
    :alt: Travis CI status

.. image:: https://coveralls.io/repos/quintagroup/collective.easyform/badge.png?branch=master
    :target: https://coveralls.io/r/quintagroup/collective.easyform?branch=master
    :alt: Coveralls status

.. image:: https://badge.fury.io/py/collective.easyform.png
    :target: http://badge.fury.io/py/collective.easyform
    :alt: Fury Python

.. image:: https://badge.fury.io/gh/quintagroup%2Fcollective.easyform.png
    :target: http://badge.fury.io/gh/quintagroup%2Fcollective.easyform
    :alt: Fury Github

.. image:: https://pypip.in/d/collective.easyform/badge.png
    :target: https://pypi.python.org/pypi/collective.easyform/
    :alt: Downloads

.. image:: https://pypip.in/v/collective.easyform/badge.png
    :target: https://pypi.python.org/pypi/collective.easyform/
    :alt: Latest Version

.. image:: https://pypip.in/wheel/collective.easyform/badge.png
    :target: https://pypi.python.org/pypi/collective.easyform/
    :alt: Wheel Status

.. image:: https://pypip.in/egg/collective.easyform/badge.png
    :target: https://pypi.python.org/pypi/collective.easyform/
    :alt: Egg Status

.. image:: https://pypip.in/license/collective.easyform/badge.png
    :target: https://pypi.python.org/pypi/collective.easyform/
    :alt: License
    
.. figure:: http://quintagroup.com/services/plone-development/products/easyform/easyform.png
    :target: https://github.com/quintagroup/collective.easyform
    :alt: Logo

Collective.easyform enables creation of custom forms using dexterity. This Plone package is similar to Products.PloneFormGen that is based on Archetypes. Dexterity is a new platform for content types in Plone and will be used instead of Archetypes in Plone 5. Easyform provides a Plone form builder through-the-web using fields, widgets, actions and validators.

Similarly to PloneFormGen, Easyform is used to generate web forms that save or mail form input. Simple and user-friendly interface allows non-programmers to create custom forms. 

Usage
=====

* Install product (in your buildout.cfg add ‘collective.easyform’ to the eggs section), rerun your Plone instance and activate Collective.easyform. 
* Choose Easyform from the 'Add new' drop-down menu. Insert form title, description and other settings.  
* Add fields or fieldsets to create a unique form that will meet your particular requirements.  There are enough basic field types to satisfy any demands: File Upload, Text line (String), Integer, Yes/No, Date, Date/Time, Floating-point number, Choice, Rich Text, Image, Multiple Choice, Text, Password, ReСaptcha field. 
* Continue to customize form by setting the order of fields, defining required and hidden ones, choosing validator, if necessary, and other field type specific settings.

See quick overview of this product: 

.. image:: http://quintagroup.com/services/plone-development/products/easyform/easyform-youtube.png
    :target: https://www.youtube.com/watch?v=DMCYnYE9RKU
    :alt: Collective.easyform

Compatibility
-------------

Plone 4.3.2
