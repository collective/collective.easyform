Integration tests
=================

::
    >>> browser = get_browser(layer)

Standalone form
---------------

Add a new EasyForm::

    >>> portal = layer['portal']
    >>> portal_url = portal.absolute_url()
    >>> browser.open(portal_url)
    >>> browser.url
    'http://nohost/plone'
    >>> browser.getLink('EasyForm').click()
    >>> browser.getControl('Title').value = 'testform'
    >>> browser.getControl('Save').click()

We'll want to test the save data adapter later.
Let's add one now::

    >>> browser.getLink('Actions').click()
    >>> browser.open(portal_url + '/testform/actions/@@add-action')
    >>> browser.getControl('Title').value = 'saver'
    >>> browser.getControl('Short Name').value = 'saver'
    >>> browser.getControl('Save Data').selected = True
    >>> browser.getControl('Add').click()
    >>> browser.open(portal_url + '/testform/actions/saver')
    >>> 'Edit' in browser.contents
    True

Return to form and confirm that it renders properly::

    >>> browser.handleErrors = False
    >>> browser.open(portal_url + '/testform')
    >>> browser.url
    'http://nohost/plone/testform'
    >>> 'testform' in browser.contents
    True

Submit the form.  An incomplete submission should give validation errors::

    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'test'
    >>> browser.getControl('Submit').click()
    >>> browser.url
    'http://nohost/plone/testform'
    >>> 'There were some errors.' in browser.contents
    True

Now let's try a complete submission and confirm that it displays the default
thank you page.  The default form has a mailer, so we'll programmatically set
a recipient so that it doesn't complain.  (The mailer is mocked in the doctest
base class)::

    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> browser.url
    'http://nohost/plone/testform'

    >>> 'Thanks for your input.' in browser.contents
    True

Add a new fieldset::

    >>> browser.getLink('Define form fields').click()
    >>> browser.getLink(id='add-fieldset').click()
    >>> browser.getControl('Title').value = 'New fieldset'
    >>> browser.getControl('Short Name').value = 'new_fieldset'
    >>> browser.getControl('Add').click()

Change fieldset of Comments field::

    >>> url = portal_url + '/testform/fields/comments/@@changefieldset?fieldset_index=1'
    >>> browser.open(url)

Submit the form::

    >>> browser.open(portal_url + '/testform/actions/mailer')
    >>> browser.getControl(name='form.widgets.recipient_email').value = 'mdummy@address.com'
    >>> browser.open(portal_url + '/testform')
    >>> browser.getControl('Your E-Mail Address').value = 'test@example.com'
    >>> browser.getControl('Subject').value = 'Test Subject'
    >>> browser.getControl('Comments').value = 'PFG rocks!'
    >>> browser.getControl('Submit').click()
    <sent mail from ...to ['mdummy@address.com']>
    >>> 'test@example.com' in browser.contents
    True
    >>> 'Test Subject' in browser.contents
    True
    >>> 'PFG rocks!' in browser.contents
    True
    >>> 'Thanks for your input.' in browser.contents
    True

The check to traverse to /news after submission has moved to non-doctest because of a weird traceback in py3::

    Error in test [...]/collective.easyform/src/collective/easyform/tests/browser.rst
    doctest.UnexpectedException: <DocTest browser.rst from [...]/collective.easyform/src/collective/easyform/tests/browser.rst:0 (95 examples)>

    AssertionError: Content-Length is different from actual app_iter length (24988!=50737)

We should be able to view an individual field::

    >>> browser.open(portal_url + '/testform/fields/comments')
    >>> browser.url
    'http://nohost/plone/testform/fields/comments'
    >>> print(browser.contents)  # doctest: +SKIP
    <!DOCTYPE...
    ...
     <div class="pfg-form formid-comments">
          ...
          <textarea...name="comments"...></textarea>
          ...
          <div class="formControls">
            ...
            <input type="hidden" name="form.submitted"
                   value="1" />
            ...
            <input class="context" type="submit"
                   name="form_submit" value="Submit" />
          </div>
      </form>
    </div>
    ...

Attempts to use gpg_services TTW should be fruitless::

    >>> browser.open(portal_url + '/testform/@@gpg_services/encrypt?data=XXX&recipient_key_id=yyy')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

Attempts to read the success action TTW should be fruitless::

    >>> browser.open(portal_url + '/testform/fgGetSuccessAction')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

That should also be true for fields::

    >>> browser.open(portal_url + '/testform/comments/fgGetSuccessAction')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

Attempts to set mailer body TTW should fail::
    >>> browser.open(portal_url + '/testform/mailer/setBody_pt?value=stuff')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

Attempts to read mailer body TTW should fail::
    >>> browser.open(portal_url + '/testform/mailer/body_pt')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

We want to test security on the custom script adapter. Let's add one::

    >>> browser.open(portal_url + '/testform')
    >>> browser.getLink('Actions').click()
    >>> browser.open(portal_url + '/testform/actions/@@add-action')
    >>> browser.getControl('Title').value = 'Test Script Adapter'
    >>> browser.getControl('Short Name').value = 'test_script_adapter'
    >>> browser.getControl('Custom Script').selected = True
    >>> browser.getControl('Add').click()
    >>> browser.open(portal_url + '/testform/actions/test_script_adapter')
    >>> browser.url
    'http://nohost/plone/testform/actions/test_script_adapter'

Attempts to set script body TTW should fail::

    >>> browser.open(portal_url + '/testform/test-script-adapter/updateScript?body=raise%2010&role=none')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

Attempts to run the script TTW should fail::

    >>> browser.open(portal_url + '/testform/test-script-adapter/onSuccess?fields=')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

    >>> browser.open(portal_url + '/testform/test-script-adapter/scriptBody?fields=')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

    >>> browser.open(portal_url + '/testform/test-script-adapter/executeCustomScript?fields=&form=&req=')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

Attempts to use onSuccess TTW should fail::

    >>> browser.open(portal_url + '/testform/saver/onSuccess?fields=&request=')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

Attempts to read our special member attributes TTW should fail::

    >>> browser.open(portal_url + '/testform/memberId')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

    >>> browser.open(portal_url + '/testform/memberFullName')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...

    >>> browser.open(portal_url + '/testform/memberEmail')
    Traceback (most recent call last):
    ...
    zExceptions.NotFound: ...
