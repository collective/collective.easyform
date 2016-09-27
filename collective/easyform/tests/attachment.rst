File attachments
================

    >>> import cStringIO
    >>> browser = self.browser

Add a new EasyForm::

    >>> browser.open(self.portal_url)
    >>> browser.getLink('EasyForm').click()
    >>> browser.getControl('Title').value = 'attachmentform'
    >>> browser.getControl('Save').click()
    >>> browser.url
    'http://nohost/plone/attachmentform/view'

We'll want to test the save data adapter later.
Let's add one now::

    >>> browser.getLink('Actions').click()
    >>> browser.open(self.portal_url + '/attachmentform/actions/@@add-action')
    >>> browser.getControl('Title').value = 'Saver'
    >>> browser.getControl('Short Name').value = 'saver'
    >>> browser.getControl('Save Data').selected = True
    >>> browser.getControl('Add').click()
    >>> browser.open(self.portal_url + '/attachmentform/actions/saver')
    >>> 'Edit' in browser.contents
    True

Add a File field::

    >>> browser.open(self.portal_url + '/attachmentform')
    >>> browser.getLink('Define form fields').click()
    >>> browser.getLink('Add new field…').click()
    >>> browser.getControl('Title').value = 'Attachment'
    >>> browser.getControl('Short Name').value = 'attachment'
    >>> browser.getControl('File Upload').selected = True
    >>> browser.getControl('Add').click()

And confirm that it renders properly::

    >>> browser.open(self.portal_url + '/attachmentform')
    >>> browser.url
    'http://nohost/plone/attachmentform...'

Submit the form with an text attachment::

    >>> browser.open(self.portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(self.portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(cStringIO.StringIO('file contents'), 'text/plain', 'test.txt')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> self.portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    'file contents'

Submit the form with an image attachment::

    >>> browser.open(self.portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(self.portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(cStringIO.StringIO('image content'), 'image/gif', 'test.gif')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> self.portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    'image content'

Submit the form with an audio attachment::

    >>> browser.open(self.portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(self.portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(cStringIO.StringIO('audio content'), 'audio/mpeg', 'test.mp3')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> self.portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    'audio content'

Submit the form with an zip attachment::

    >>> browser.open(self.portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(self.portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(cStringIO.StringIO('zip content'), 'application/zip', 'test.zip')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> self.portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    'zip content'

Excluded fields
---------------

Make sure the attachment is not included in the email if showAll is False and
the file field is not listed in the mailer's showFields::

    >>> browser.open(self.portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl('Include All Fields').selected = False
    >>> browser.getControl('Save').click()
    >>> self.portal.MailHost.msg = None

    >>> browser.open('http://nohost/plone/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(cStringIO.StringIO('file contents'), 'text/plain', 'test.txt')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> self.portal.MailHost.msg.get_payload(decode=True)
    '<html xmlns="http://www.w3.org/1999/xhtml">\n  <head><title></title></head>\n  <body>\n    <p></p>\n    <dl>\n        \n    </dl>\n    <p></p>\n    <pre></pre>\n  </body>\n</html>'

    >> browser.getControl('Reset').click()

Saved data
----------

Check saved data::

    >>> browser.getLink('Saved data').click()
    >>> 'http://nohost/plone/attachmentform/actions/saver/data' in browser.contents
    True
    >>> browser.getLink('Saver').click()
    >>> "5 input(s) saved" in browser.contents
    True
    >>> ".widgets.attachment/@@download/test.gif" in browser.contents
    True
    >>> ".widgets.attachment/@@download/test.mp3" in browser.contents
    True
    >>> ".widgets.attachment/@@download/test.zip" in browser.contents
    True
    >>> ".widgets.attachment/@@download/test.txt" in browser.contents
    True
    >>> '<input id="crud-edit-form-buttons-edit" name="crud-edit.form.buttons.edit" class="submit-widget button-field" value="Apply changes" type="submit" />' in browser.contents
    True
    >>> '<input id="crud-edit-form-buttons-delete" name="crud-edit.form.buttons.delete" class="submit-widget button-field" value="Delete" type="submit" />' in browser.contents
    True
    >>> '<input id="form-buttons-download" name="form.buttons.download" class="submit-widget button-field" value="Download" type="submit" />' in browser.contents
    True
    >>> '<input id="form-buttons-clearall" name="form.buttons.clearall" class="submit-widget button-field" value="Clear all" type="submit" />' in browser.contents
    True
    >>> browser.getLink('test.txt').click()
    >>> browser.url
    'http://nohost/plone/attachmentform/@@actions/saver/data/++widget++crud-edit...widgets.attachment/@@download/test.txt'
    >>> browser.contents
    'file contents'
    >>> browser.goBack()
    >>> def first_item(browser, type_="checkbox"):
    ...     for form in browser.mech_browser.forms():
    ...         for control in form.controls:
    ...             if control.type == type_ and control.name.startswith('crud-edit.'):
    ...                 return control.name
    ...
    >>> fcb = browser.getControl(name=first_item(browser))
    >>> fcb.value = fcb.options
    >>> browser.getControl("Delete").click()
    >>> "Successfully deleted items." in browser.contents
    True
    >>> "4 input(s) saved" in browser.contents
    True
    >>> browser.getControl(name=first_item(browser, 'text')).value = "testingchangingemail@mail.com"
    >>> browser.getControl("Apply changes").click()
    >>> "Successfully updated" in browser.contents
    True
    >>> "4 input(s) saved" in browser.contents
    True
    >>> browser.getControl("Clear all").click()
    >>> "0 input(s) saved" in browser.contents
    True
    >>> browser.getControl("Download").click()


