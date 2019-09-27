File attachments
================

    >>> from six import BytesIO
    >>> browser = get_browser(layer)

Add a new EasyForm::

    >>> portal_url = layer['portal'].absolute_url()
    >>> browser.handleErrors = False
    >>> browser.open(portal_url)
    >>> browser.getLink('EasyForm').click()
    >>> browser.getControl('Title').value = 'attachmentform'
    >>> browser.getControl('Save').click()
    >>> browser.url
    'http://nohost/plone/attachmentform/view'

We'll want to test the save data adapter later.
Let's add one now::

    >>> browser.getLink('Actions').click()
    >>> browser.open(portal_url + '/attachmentform/actions/@@add-action')
    >>> browser.getControl('Title').value = 'Saver'
    >>> browser.getControl('Short Name').value = 'saver'
    >>> browser.getControl('Save Data').selected = True
    >>> browser.getControl('Add').click()
    >>> browser.open(portal_url + '/attachmentform/actions/saver')
    >>> 'Edit' in browser.contents
    True

Add a File field::

    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.getLink('Define form fields').click()
    >>> browser.getLink(id='add-field').click()
    >>> browser.getControl('Title').value = 'Attachment'
    >>> browser.getControl('Short Name').value = 'attachment'
    >>> browser.getControl('File Upload').selected = True
    >>> browser.getControl('Add').click()

And confirm that it renders properly::

    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.url
    'http://nohost/plone/attachmentform...'

Submit the form with an text attachment::

    >>> browser.open(portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(BytesIO(b'file contents'), 'text/plain', 'test.txt')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> portal = layer['portal']
    >>> portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    b'file contents'

Submit the form with an image attachment::

    >>> browser.open(portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(open(get_image_path(), 'rb'), 'image/png', 'test.png')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xb4\x00\x00\x00/\x08\x06\x00\x00\x00Jl\xe0\xb2\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x10\xa8IDATx\x9c\xed\x9d{xT\xd5\xb5\xc0\x7f\xeb\x9c\t\t \xf8\xa0BQ\xd0\x86IxH}]\xad\xb6^\xad\x8f\xa2\xb4\x96\xaaU\xc1\x07>\x9a\x07\xc6\x8b\x8fj\xd5\xab\xb6\xda\xc6\xf7\xf5Q\xfba\xc5\x162\x93\x88\xd7\xf6r\xa3\xe2\x93\xab\xf7\x93[D[\xabT' in portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    True

Submit the form with an audio attachment::

    >>> browser.open(portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(BytesIO(b'audio content'), 'audio/mpeg', 'test.mp3')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    b'audio content'

Submit the form with an zip attachment::

    >>> browser.open(portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(BytesIO(b'zip content'), 'application/zip', 'test.zip')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True

Make sure the attachment was included in the email message::


    >>> portal.MailHost.msg.get_payload()[1].get_payload(decode=True)
    b'zip content'

Excluded fields
---------------

Make sure the attachment is not included in the email if showAll is False and
the file field is not listed in the mailer's showFields::

    >>> browser.open(portal_url + '/attachmentform/actions/mailer')
    >>> browser.getControl('Include All Fields').selected = False
    >>> browser.getControl('Save').click()
    >>> portal.MailHost.msg = None

    >>> browser.open('http://nohost/plone/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(BytesIO(b'file contents'), 'text/plain', 'test.txt')
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> portal.MailHost.msg.get_payload(decode=True)
    b'<html xmlns="http://www.w3.org/1999/xhtml">\n  <head><title></title></head>\n  <body>\n    <p></p>\n    <dl>\n        \n    </dl>\n    <p></p>\n    <p></p>\n  </body>\n</html>'

    >> browser.getControl('Reset').click()

Saved data
----------

Check saved data::

    >>> browser.getLink('Saved data').click()
    >>> 'http://nohost/plone/attachmentform/actions/saver/@@data' in browser.contents
    True
    >>> browser.getLink('Saver').click()
    >>> "5 input(s) saved" in browser.contents
    True
    >>> ".widgets.attachment/@@download/test.png" in browser.contents
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
    'http://nohost/plone/attachmentform/@@actions/saver/@@data/++widget++crud-edit...widgets.attachment/@@download/test.txt'
    >>> browser.contents
    'file contents'
    >>> browser.goBack()
    >>> def first_item(browser, type_="checkbox"):
    ...     form = browser.getForm(index=1)
    ...     controls = form.controls if hasattr(form, 'controls') else form.mech_form.controls
    ...     for control in controls:
    ...         if getattr(control, 'type', None) == type_ and control.name.startswith('crud-edit.'):
    ...             return control.name
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


Test file uploads with non ASCII characters in the title

    >>> browser.open(portal_url + '/attachmentform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = u'München'.encode('utf-8')
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl(name='form.widgets.attachment').add_file(BytesIO(b'file contents'), 'text/plain', u'Zürich.txt'.encode('utf-8'))
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'Thanks for your input.' in browser.contents
    True
    >>> from collective.easyform.api import get_actions
    >>> saver = get_actions(layer['portal']['attachmentform'])['saver']
    >>> print(saver.getSavedFormInputForEdit())
    test@example.com,München,PFG rocks!,Zürich.txt
    <BLANKLINE>


