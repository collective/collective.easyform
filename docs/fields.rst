Fields
======

Adding new field
----------------

.. image:: images/click-fields-contentview.png

.. image:: images/created-easyform-fields.png

.. image:: images/click-add-new-field.png

.. image:: images/add-new-field-overlay.png

.. image:: images/added-new-field.png

Adding new fieldset
-------------------

.. image:: images/click-add-new-fieldset.png

.. image:: images/add-new-fieldset-overlay.png

.. image:: images/added-new-fieldset.png

Edit field
----------

.. image:: images/created-easyform-fields.png

Edit XML Fields Model
---------------------

.. image:: images/edit-xml-fields-model-button.png

.. image:: images/edit-xml-fields-model-page.png

Validating fields
-----------------

For validation of filesize put the following line into
the custom validator of a file upload field:

 `python:portal.restrictedTraverse('validate_file_size')(value, size=300)` 

where `size` is the maximum allowed size in bytes.

