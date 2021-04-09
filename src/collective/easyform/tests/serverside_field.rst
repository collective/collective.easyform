Server-side only field
----------------------

Get our test browser::

    >>> browser = get_browser(layer)
    >>> portal = layer['portal']
    >>> portal_url = portal.absolute_url()
    >>> browser.open(portal_url)

Add a new form folder and mark the subject input variable as a server side variable.
(It needs a non-empty default value because it's set as required.) ::

    >>> browser.getLink('EasyForm').click()
    >>> browser.getControl('Title').value = 'testform'
    >>> browser.getControl('Save').click()
    >>> 'Item created' in browser.contents
    True
    >>> browser.open(portal_url + '/testform/fields/topic')
    >>> browser.getControl('Server-Side Variable').selected = True
    >>> browser.getControl('Default Expression').value = 'string:asdf'
    >>> browser.getControl('Save').click()

And confirm that the server-side field is absent from the rendered form::

    >>> browser.open(portal_url + '/testform')
    >>> 'id="form-widgets-topic"' in browser.contents
    False

By default when we submit the form the server-side field won't be included on the
thank you page::

    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Comments').value = 'Now with double the rockage...'
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>

    >>> 'Subject' in browser.contents
    False

Test for 'Subject' in the mail body::

    >>> msgtext = portal.MailHost.msgtext[portal.MailHost.msgtext.index(b'\n\n'):]
    >>> body = b'\n\n'.join(portal.MailHost.msgtext.split(b'\n\n')[1:])
    >>> b'Subject' in body
    False

Specifically list the field as one that should be included in the thank
you page, and then it should show up in mail and thanks page.

TODO: Since getform('xy').mech_form isn't available anymore we have to move this to a robottest
::

#    >>> browser.open(portal_url + '/testform/edit')
#    >>> browser.getControl('Show All Fields').selected = False
#    >>> browser.getForm(id="form").mech_form.new_control(type='hidden', name='form.widgets.showFields:list', attrs=dict(value='topic'))
#    >>> browser.getControl('Save').click()
#    >>> 'Changes saved' in browser.contents
#    True
#    >>> browser.open(portal_url + '/testform/actions/mailer')
#    >>> browser.getControl('Include All Fields').selected = False
#    >>> browser.getForm(id="form").mech_form.new_control(type='hidden', name='form.widgets.showFields:list', attrs=dict(value='topic'))
#    >>> browser.getControl('Save').click()
#    >>> browser.open(portal_url + '/testform')
#    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
#    >>> browser.getControl('Comments').value = 'Now with double the rockage...'
#    >>> browser.getControl('Submit').click()
#    <sent mail from ...to ['mdummy@address.com']>

#    >>> portal = layer['portal']
#    >>> body = '\n\n'.join(portal.MailHost.msgtext.split('\n\n')[1:])
#    >>> 'Subject' in body
#    True

#    >>> portal.testform.showAll
#    False
#    >>> print(portal.testform.showFields)
#    ['topic']

#    >>> 'Subject' in browser.contents
#    True
