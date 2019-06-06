Changelog
=========

1.0a4 (unreleased)
------------------

New:

- Add 'easyform-thankspage' css class to the content-core div if the thankspage is 
  displayed. Combined with the header_injection field you can style elements
  only for the thankspage, for example as a workaround to remove empty
  fieldsets (#154). [fredvd]

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

Fixes:

- Fix validation and inline validation for fields in fieldsets. Refs #172. [frevd]

- Fix inline validation. Backport for 1.x from #59 . Possibly also closes #5 (running spinner). [tomgross, fredvd]

- Fixed errors with ``header_injection`` implementation. [maurits]

- Add missing ``header_injection`` implementation. Backport for 1.x from #152. [krissik, fredvd]

- Fixed filtering of fields on thanks page and mailer template.
  We show the correct fields now.  In the mailer, the order is also what we selected.
  [maurits]

- fix plone.schemaeditor i18n factory import. This fixes 5.0.1 support

- Reverted some Plone 5 fixes that prevented collective.easyform from working
  anymore on Plone 4.3, in particular some modals/overlays. [fredvd]

- Pin to plone.schemaeditor 2.0.7 in setup.py, lower and higher versions break
  on Plone 4.3. See #30 [fredvd]


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
