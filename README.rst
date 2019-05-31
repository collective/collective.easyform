Introduction
============

.. image:: https://travis-ci.org/collective/collective.easyform.png?branch=master
    :target: https://travis-ci.org/collective/collective.easyform
    :alt: Travis CI status

.. image:: https://coveralls.io/repos/collective/collective.easyform/badge.svg?branch=master
    :target: https://coveralls.io/r/collective/collective.easyform?branch=master
    :alt: Coveralls status

.. image:: https://badge.fury.io/py/collective.easyform.svg
    :target: http://badge.fury.io/py/collective.easyform
    :alt: Fury Python
    
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
