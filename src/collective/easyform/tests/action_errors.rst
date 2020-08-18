Create a new EasyForm::

    >>> browser = get_browser(layer)
    >>> portal = layer['portal']
    >>> portal_url = portal.absolute_url()
    >>> browser.open(portal_url)
    >>> browser.url
    'http://nohost/plone'
    >>> browser.getLink('EasyForm').click()
    >>> browser.getControl('Title').value = 'testform'
    >>> browser.getControl('Save').click()

We want to test errors created by actions. Start by adding
a custom script adapter::

    >>> browser.getLink('Actions').click()
    >>> browser.open(portal_url + '/testform/actions/@@add-action')
    >>> browser.getControl('Title').value = 'custom'
    >>> browser.getControl('Short Name').value = 'custom'
    >>> browser.getControl('Custom Script').selected = True
    >>> browser.getControl('Add').click()
    >>> browser.open(portal_url + '/testform/actions/custom')
    >>> 'Edit' in browser.contents
    True

First, make the script a noop::

    >>> browser.open(portal_url + '/testform/actions/custom')
    >>> browser.getControl('Script body').value = 'pass'
    >>> browser.getControl('Save').click()

Submit the form::

    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'Hello, world!'
    >>> browser.getControl('Submit').click()
    <sent mail from  to ['mdummy@address.com']>
    >>> browser.url
    'http://nohost/plone/testform'
    >>> 'Thanks for your input.' in browser.contents
    True

Let's raise a field error in the script adapter by returing
a dictionary::

    >>> browser.open(portal_url + '/testform/actions/custom')
    >>> browser.getControl('Script body').value = 'return {"comments": "field error"}'
    >>> browser.getControl('Save').click()

Submit the form::

    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'Hello, world!'
    >>> browser.getControl('Submit').click()
    <sent mail from  to ['mdummy@address.com']>
    >>> browser.url
    'http://nohost/plone/testform'
    >>> 'Thanks for your input.' in browser.contents
    False
    >>> 'There were some errors.' in browser.contents
    True
    >>> 'field error' in browser.contents
    True

Repeat the test but move the script in front of the mailer. No email
is sent anymore (note the missing "sent mail" at the end)::

    >>> browser.post(portal_url + '/testform/actions/custom/@@order', 'pos=0&fieldset_index=0')
    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'Hello, world!'
    >>> browser.getControl('Submit').click()

Finally, we can also generate an error not attached to a field
(when creating own action adapters, FORM_ERROR_MARKER is available
as a constant at collective.easyform.config)::

    >>> browser.open(portal_url + '/testform/actions/custom')
    >>> browser.getControl('Script body').value = 'return {request.FORM_ERROR_MARKER: "form error"}'
    >>> browser.getControl('Save').click()

It replaces the generic form error message::

    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Comments').value = 'Hello, world!'
    >>> browser.getControl('Submit').click()
    >>> browser.url
    'http://nohost/plone/testform'
    >>> 'Thanks for your input.' in browser.contents
    False
    >>> 'There were some errors.' in browser.contents
    False
    >>> 'form error' in browser.contents
    True

The generic form error message can be combined with field errors
by returning a dictionary with several entries in the onSuccess
method of your (own) form action.
