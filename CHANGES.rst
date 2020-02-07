Changelog
=========

2.1.4 (2020-02-06)
------------------

- Add 'easyform-thankspage' css class to the content-core div if the thankspage is 
  displayed. Combined with the header_injection field you can style elements
  only for the thankspage, for example as a workaround to remove empty
  fieldsets (#154).
  [fredvd]

- do not append the re-rendered download form when generating the
  data download file (#175)
  [mamico, tkimnguyen]

- fix Travis install of google-chrome-stable
  [tkimnguyen]

- PEP8 fixes
  [mamico]

2.1.3 (2019-12-11)
------------------

- Brazilian Portuguese translation `#200 <https://github.com/collective/collective.easyform/issues/200>`_
  [ericof]


2.1.2 (2019-11-18)
------------------

- Fix broken image in README (partly addresses #197)
  [tkimguyen]

- Mention reCAPTCHA V2 when obtaining public/private key pair
  [tkimnguyen]


2.1.1 (2019-11-18)
------------------

NOTE: if you deploy 2.1.1+, the easyform extended validations start working again on fields
in extra field sets (they only worked on the main/default fields). This could cause some
issues if those validators, or default values, were misconfigured in the first place.

- Let ``filter_fields`` return fields in the correct order.
  This fixes the order on the default mailer template.
  Part of `issue #163 <https://github.com/collective/collective.easyform/issues/163>`_.
  [maurits]

- Fixed validation, inline validation, and defaults for fields in fieldsets.
  Refs issues `#172 <https://github.com/collective/collective.easyform/issues/172>`_
  and ` #157 <https://github.com/collective/collective.easyform/issues/157>`_. [fredvd, maurits]

- Moved from dotted to named behaviors.
  [iham]

- Avoid potential CannotGetPortalError on startup #164
  [laulaz]

- Add collective.z3cform.norobots integration #145
  [1letter/gomez]

- For CSV and XML attachments send an empty string if the value is None instead of the string "None"
  [nngu6036]

- Put in tests to show recaptcha validation prevents submissions
  [djay]

- Fix UnicodeDecodeError while attaching an image to a mail #187
  [krissik]

- update instructions for recaptcha functionality
  [tkimnguyen]

2.1.0 (2019-04-25)
------------------

New features:

- Code style black & isort.
  [jensens]

- Add "CheckBoxFieldWidget" for Multi-Choice-Field and "RadioFieldWidget" for Single-Choice-Field
  [petschki]

- add ``plone.formwidget.recaptcha`` to test dependencies
  [petschki]

- Added style bundle with content type icon for toolbar and folder_contents
  [agitator]

- nicer representation of complex field types such as bools and dates when serialized to XML or CSV attachments
  [nngu6036]

Bug fixes:

- fix bug where lines longer than 998 in XML or CSV attachmentments can get wrapped
  [nngu6036]

- add missing ``header_injection`` implementation
  [krissik]


2.1.0rc1 (2019-03-19)
---------------------

New features:

- Add Support for Python 3.
  [pbauer]

- a11y: Added role attribute for portalMessage
  [nzambello]

Bug fixes:

- fixed startup ResourceWarning on open files
  [ajung]

2.0.1 (2018-12-04)
------------------

- Spanish translation.
  [erral]


2.0.0 (2018-10-03)
------------------

New features:

- New method in api: filter_widgets. If a isn't selected, mailer action don't try
  to render its widget. This is useful when we want to avoid to show some widgets
  like recaptcha, that could breaks if it's in the wrong context.
  [cekk]

Bug fixes:

- changed the permission of saveddata action from "Manage portal" to "Modify portal content" so "action" and "view" have the same permission
  [eikichi18]

- Fix to thanks page regression introduced in 2.0.0b4
  [instification]

- Fix e-mail attachments with non ASCII chars
  [tomgross]

2.0.0b7 (2018-09-01)
--------------------

- Add option to attach form data in XML format to email
  [nngu6036]

- add some mailer adapter documentation, add required package version pins
  [tkimnguyen]


2.0.0b6 (2018-08-20)
--------------------

- Bug fixes:

- update some old documentation, add documentation for @@get_save_data_adapters view
  [tkimnguyen]


New features:

- add @@get_save_data_adapters view
  [tkimnguyen]


2.0.0b5 (2018-06-22)
--------------------

Bug fixes:

- Fix display of items in fieldset on thanks page
  [tomgross]


2.0.0b4 (2018-05-17)
--------------------

New features:

- Add support for hidden fields
  [tomgross]


Bug fixes:

- Fix filtering regression introduced with 2.0.0b3
  [tomgross]


2.0.0b3 (2018-05-08)
--------------------

New features:

- Add browserlayer.
  [jensens]

- Enhance file validation view with type check
  [tomgross]

- Basque translation
  [erral]

- Update italian translations.
  [arsenico13]

- Allow default fields, actions & mailtemplate in DB
  [tomgross]

- New mailer adapter checkbox to send CSV data attachment
  [tkimnguyen]

Bug fixes:

- Do not override configured widgets with default widgets in thank-you-page.
  This fixes #111. Includes code cleanup.
  [jensens]

- Hide profiles not used for regular install.
  [jensens]

- Remove ProtectedEmail and ProtectedTextLine  as addable fields
  https://github.com/collective/collective.easyform/issues/94
  [fgrcon]

- Support ``showAll`` and ``includeEmpties`` also for the thanks page.
  [thet]

- Register the recaptcha validator more specifically, so that it overrides the default easyform validator.
  Fixes an issue where plone.formwidget.recaptcha had no effect when used.
  [thet]

- Fix broken access to saved data due to acquisition problems if action is called 'data'.
  Fixes: #87.
  [sverbois]

- Fix action URLs to savedata, export, import
  [tomgross]

- Fix display of values in mailer template  #76
  [tomgross]


2.0.0b2 (2017-08-31)
--------------------

Bug fixes:

- Update italian translations.
  [arsenico13]

- Added Products.validation dependency to make it work for archetypes-free sites.
  [agitator]

- In the schema editor for fields, Fix the URL to ACE library according to the modeleditor in plone.app.dexterity.
  [thet]

- Fix saver action with non ASCII filename uploads #77
  [tomgross]

- In the schema editor for fields, Fix the URL to ACE library according to the modeleditor in plone.app.dexterity.
  [thet]

2.0.0b1 (2017-06-14)
--------------------

New features:

- Add filesize upload validator
  [tomgross]

Bug fixes:

- Take over signature linebreaks to HTML email
  [tomgross]

- Allow multi-select fields as subject field
  https://github.com/collective/collective.easyform/issues/71
  [tomgross]

- Update german translations.
  [tomgross, jensens]

- Keep line breaks for body_pre, body_post and body_footer field.
  Changed field type to RichText with TextAreaWidget and default_mime_type='text/x-web-intelligent'.
  Updated default mailer template.
  [agitator]

- Use site email address as default recipient address also for Plone 5.
  [tmassman]

- Update README
  [svx]

- Allow emails (CC, BCC) separated by ';' and newlines
  https://github.com/collective/collective.easyform/issues/49
  [tomgross]

- Allow managment of fields enabled for c.easyform in controlpanel
  [karalics]


2.0.0a2 (2016-10-14)
--------------------

New:

- Rename api.get_fields to api.get_schema
  [jensens, agitator]

Fixes:

- Fix field order
  [jensens, agitator]


2.0.0a1 (2016-10-13)
--------------------

New:

- Update for Plone 5, no longer support Plone 4.x
  [agitator]

Fixes:

- Fix: Overhaul TravisCI setup to really use caches.
  Use bobtemplates.plone travis setup as best practice.
  [jensens]

- Don't show the reset button after form submission at the summary page.
  [thet]

- Housekeeping: isort, zca decorators, autopep8 and major manual cleanup.
  Includes structural cleanup and
  [jensens, agitator]


1.0a4 (unreleased)
------------------

New:

- Change recipient address field to Email type so it gets properly validated
  [davilima6]

- Make the default buildout use Plone 5. Update travis setup to the point where
  tests actually run, though many still fail.
  [smcmahon]


- look up email_from_address in registry
  [kcleong]

- Move the default xml configuration out into xml files. These can be picked up
  by ``i18ndude`` or other po file generators for translations strings. Also
  translate the ``FIELDS_DEFAULT`` fields.
  [thet]

- Add German translations.
  [thet]

- Allow the definition of some EasyForm default values via the i18n translation
  mechanism.
  [thet]

- Reworked mail address formating, avoiding recipient address in the form of
  ``name <<account@domain.com>>`` and having instead
  ``name <account@domain.com>``.
  [thet]

- Depend on plone.schemaeditor > 2.0 for JS compatibility.
  [thet]

- fix plone.schemaeditor i18n factory import. This fixes 5.0.1 support.
  [vangheem]

- Fix modeleditor.pt markup so it works with barceloneta.
  [ebrehault]

Fixes:

- fix plone.schemaeditor i18n factory import. This fixes 5.0.1 support


1.0a3 (2015-06-02)
------------------

- Fixed templates
  [kroman0]

- Fixed field order #17
  [kroman0]

- Fixed Plone 5 support
  [kroman0]

- Fixed dependencies
  [kroman0]

- Set script type correctly
  [fredvd]


1.0a2 (2014-06-13)
------------------

- Fixed conflict with plone.app.multilingual[dexterity]
  [kroman0]

- Fixed rendering saved data form
  [kroman0]

- Fixed and updated tests
  [kroman0]

- Fix unicode encoding in download csv
  [gborelli]

- Added Italian translation
  [gborelli]

- Added fields parameter in Mailer override expressions
  [gborelli]


1.0a1 (2014-03-18)
------------------

- Initial release
