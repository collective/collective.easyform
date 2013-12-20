The Formulator content type
===============================

In this section we are tesing the Formulator content type by performing
basic operations like adding, updadating and deleting Formulator content
items.

    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser = self.browser
    >>> portal_url = self.portal_url
    >>> browser.open(portal_url)

Adding a new Formulator content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Formulator' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Formulator').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Formulator' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl('Title').value = 'Formulator Sample'
    >>> browser.getControl('Save').click()
    >>> 'Item created' in browser.contents
    True

And we are done! We added a new 'Formulator' content item to the portal.

Updating an existing Formulator content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl('Title').value = 'New Formulator Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Formulator Sample' in browser.contents
    True

Removing a/an Formulator content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Formulator
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Formulator Sample' in browser.contents
    True

Now we are going to delete the 'New Formulator Sample' object. First we
go to the contents tab and select the 'New Formulator Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Formulator Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Formulator
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Formulator Sample' in browser.contents
    False

Adding a new Formulator content item as contributor
------------------------------------------------

Not only site managers are allowed to add Formulator content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Formulator' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Formulator').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Formulator' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl('Title').value = 'Formulator Sample'
    >>> browser.getControl('Save').click()
    >>> 'Item created' in browser.contents
    True

Done! We added a new Formulator content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


