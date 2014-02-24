The EasyForm content type
===============================

In this section we are tesing the EasyForm content type by performing
basic operations like adding, updadating and deleting EasyForm content
items.

    >>> browser = self.browser
    >>> portal_url = self.portal_url
    >>> browser.open(portal_url)

Adding a new EasyForm content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'EasyForm' and click the 'Add' button to get to the add form.

    >>> browser.getControl('EasyForm').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'EasyForm' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl('Title').value = 'EasyForm Sample'
    >>> browser.getControl('Save').click()
    >>> 'Item created' in browser.contents
    True

And we are done! We added a new 'EasyForm' content item to the portal.

Updating an existing EasyForm content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl('Title').value = 'New EasyForm Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New EasyForm Sample' in browser.contents
    True

Removing a/an EasyForm content item
--------------------------------

If we go to the home page, we can see a tab with the 'New EasyForm
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New EasyForm Sample' in browser.contents
    True

Now we are going to delete the 'New EasyForm Sample' object. First we
go to the contents tab and select the 'New EasyForm Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New EasyForm Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New EasyForm
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New EasyForm Sample' in browser.contents
    False

Adding a new EasyForm content item as contributor
------------------------------------------------

Not only site managers are allowed to add EasyForm content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'EasyForm' and click the 'Add' button to get to the add form.

    >>> browser.getControl('EasyForm').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'EasyForm' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl('Title').value = 'EasyForm Sample'
    >>> browser.getControl('Save').click()
    >>> 'Item created' in browser.contents
    True

Done! We added a new EasyForm content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()


