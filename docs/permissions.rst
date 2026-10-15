Permissions and roles
=====================

EasyForm configures the following permission assignments in
``src/collective/easyform/profiles/default/rolemap.xml``.
All permission names in the table have the prefix ``collective.easyform:``;
for example, "Download Saved Input" means
``collective.easyform: Download Saved Input``.

"Yes" indicates an explicit grant to that role in the default profile.
"--" means that the profile does not grant the permission to that role.
Roles not listed, including Anonymous and Member, receive no explicit grants
from this role map.

+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Permission            | Contributor | Editor | Owner | Reviewer | Site Administrator | Manager |
+=======================+=============+========+=======+==========+====================+=========+
| Add Content           | Yes         | --     | Yes   | --       | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Add Mailers           | --          | Yes    | Yes   | --       | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Add Data Savers       | --          | Yes    | Yes   | --       | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Download Saved Input  | --          | --     | Yes   | Yes      | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Edit Advanced Fields  | --          | Yes    | Yes   | --       | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Edit Mail Addresses   | --          | Yes    | Yes   | --       | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Edit Technical Fields | --          | --     | --    | --       | Yes                | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Add Custom Scripts    | --          | --     | --    | --       | --                 | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Edit TALES Fields     | --          | --     | --    | --       | --                 | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Edit Python Fields    | --          | --     | --    | --       | --                 | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+
| Edit Encryption Specs | --          | --     | --    | --       | --                 | Yes     |
+-----------------------+-------------+--------+-------+----------+--------------------+---------+

In particular:

* Reviewers can download saved form data through the
  ``collective.easyform: Download Saved Input`` permission.
  Owners, Site Administrators and Managers also have this permission.
* Editors can add mailers and data savers, edit advanced fields and edit mail
  addresses. The Editor role alone grants neither "Add Content" nor
  "Download Saved Input".
* Adding custom scripts, editing TALES or Python fields, and editing encryption
  specifications are granted only to Managers by this profile.

Effective permissions and customization
---------------------------------------

All permissions in this role map use ``acquire="True"``, so permission grants
can also be inherited from parent objects. Users can have multiple roles,
including local roles on a form or its parent folder; their effective access
can therefore exceed the grants shown for a single role in this table.
Workflow settings and site-specific permission customizations can also affect
access. Other Plone permissions, such as viewing or modifying content, are
outside the scope of this table and may be required for an operation.

Integrators can configure different assignments in their own GenericSetup
profile's ``rolemap.xml``. Use the full permission names, including the
``collective.easyform:`` prefix, and review acquisition and local role
assignments when checking access to a particular form.

Upgrading existing sites
------------------------

New installations receive these assignments from the default profile.
For existing installations, the upgrade from profile version 1017 to 1018
adds the Editor grants listed above and the Reviewer grant for downloading
saved input. Run the EasyForm upgrade in the Add-ons control panel to apply
these changes. The upgrade role map is in
``src/collective/easyform/upgrades/profiles/1018/rolemap.xml``.
