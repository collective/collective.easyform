Changelog
=========

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
