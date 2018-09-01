Actions
=======

Adding new action
-----------------

.. image:: images/click-actions-contentview.png

.. image:: images/created-easyform-actions.png

.. image:: images/click-add-new-action.png

.. image:: images/add-new-action-overlay.png

.. image:: images/added-new-action.png

Edit action
-----------

.. image:: images/created-easyform-actions.png

Edit XML Actions Model
----------------------

.. image:: images/edit-xml-actions-model-button.png

.. image:: images/edit-xml-actions-model-page.png

Save data adapter
-----------------

The Save Data adapter saves data submitted to a form. You can export the saved data as a comma-separated values (CSV)
or a tab-separated values (TSV) file. You can view the saved data and edit it.

If you need programmatic access to the saved data, e.g. to display the number of saved data rows for a given form,
use the `@@get_save_data_adapters` view. The following `count_items` page template displays the number of saved data
rows for all save data adapters for a given form by calling the `@@get_save_data_adapters` view then, for each
save data adapter it returns, outputting its ID and the number of rows it contains.

::

    <html>
      <head>
        <title tal:content="template/title">The title</title>
        <meta http-equiv="content-type" content="text/html;charset=utf-8">
      </head>
      <body>

        The form with ID <span tal:content="here/id">[form id]</span> contains the following save data adapters:

        <ul>
            <div tal:define="adapters here/get_save_data_adapters" tal:repeat="adapter adapters">

                <li>
                    <span tal:content="adapter/getName">ID</span>: <span tal:content="adapter/itemsSaved">[item count]</span> items
                </li>

            </div>
        </ul>

      </body>
    </html>

This is what `count_items` outputs:

::

    The form with ID <span>ff1</span> contains the following save data adapters:
    <ul>
    <div>
    <li>
    <span>save_data</span>: <span>6</span> items
    </li>
    </div>
    <div>
    <li>
    <span>save_data_2</span>: <span>2</span> items
    </li>
    </div>
    </ul>


Mailer Adapter
--------------

When you create an EasyForm, it includes a mailer adapter action that is activated by default.

You can view an EasyForm's actions by clicking on the Actions toolbar menu, choosing "Define form actions".

.. image:: images/define-actions-menu-choice.png

You can view and change the settings of that mailer by clicking on its "Settings..." link.

.. image:: images/default-actions-mailer.png

In the mailer's settings, the "Message" tab contains checkboxes that let you send submitted data as a CSV or XML file attachment.

.. image:: images/mailer-adapter-message-settings.png