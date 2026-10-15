"""Regenerate the documentation screenshots against a running Plone site.

The site needs collective.easyform installed and a user that may add
content at the site root. Nothing else is required: the script creates a
demo form, walks through the fields and actions views, submits the form
once and removes the demo form again at the end.

Run it from the package root, it only needs playwright and a Chrome or
Chromium that playwright can drive (``--channel`` picks an installed
browser, otherwise run ``playwright install chromium`` once)::

    uvx --with playwright python docs/make_screenshots.py \
        --url http://localhost:8080/Plone --user admin --password admin

The screenshots are written to ``docs/images``. They are taken at a
1200px wide viewport; keep that so the images stay consistent.
"""

import argparse
import pathlib
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sys.exit(
        "playwright is required: pip install playwright (or uvx --with playwright)"
    )


HERE = pathlib.Path(__file__).resolve().parent
FORM_ID = "contact-form"
VIEWPORT = {"width": 1200, "height": 800}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", required=True, help="URL of the Plone site")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--out", default=str(HERE / "images"), help="target directory for the PNGs"
    )
    parser.add_argument(
        "--channel",
        default="chrome",
        help='installed browser to use ("chrome", "msedge", "chromium", ...)',
    )
    parser.add_argument("--headed", action="store_true", help="show the browser")
    return parser.parse_args()


class Shooter:
    def __init__(self, page, site_url, out_dir):
        self.page = page
        self.site_url = site_url.rstrip("/")
        self.form_url = f"{self.site_url}/{FORM_ID}"
        self.out_dir = pathlib.Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    # -- helpers -----------------------------------------------------------

    def shot(self, name, clip=None, full_page=False):
        path = self.out_dir / f"{name}.png"
        self.page.screenshot(path=str(path), clip=clip, full_page=full_page)
        print("  wrote", path.name)

    def goto(self, path):
        url = path if path.startswith("http") else f"{self.form_url}/{path}"
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def modal(self):
        """The currently open pat-plone-modal."""
        modal = self.page.locator(".modal:visible").first
        modal.wait_for(state="visible")
        self.page.wait_for_timeout(600)  # let the modal finish its animation
        return modal

    def settings_link(self, name):
        """The "Settings..." link of a field or action in a listing."""
        row = self.page.locator(".fieldLabel", has_text=name).first.locator("..")
        return row.get_by_role("link", name="Settings")

    def add_in_modal(self, link, title, type_label, type_field):
        """Open an "Add new ..." modal and fill it in. The short name is
        derived from the title by plone.schemaeditor's JavaScript."""
        self.page.locator(link).first.click()
        modal = self.modal()
        modal.get_by_label("Title").fill(title)
        modal.get_by_label(type_field).select_option(label=type_label)
        self.page.wait_for_timeout(300)
        return modal

    def submit_modal(self, modal, button="Add"):
        modal.get_by_role("button", name=button).first.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(800)

    def close_modal(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def click_tab(self, label):
        # the accessible name of a tab may carry the "required" marker
        self.page.get_by_role("link", name=label).first.click()
        self.page.wait_for_timeout(300)

    # -- steps -------------------------------------------------------------

    def login(self, user, password):
        self.page.goto(f"{self.site_url}/login")
        self.page.get_by_label("Login Name").fill(user)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role("button", name="Log in").click()
        self.page.wait_for_load_state("networkidle")

    def remove_demo_form(self):
        self.page.goto(f"{self.form_url}/delete_confirmation")
        if self.page.locator(
            "form#delete_confirmation, form.pat-formautofocus"
        ).count():
            self.page.get_by_role("button", name="Delete").first.click()
            self.page.wait_for_load_state("networkidle")

    def add_new_menu(self):
        self.page.goto(self.site_url)
        self.page.wait_for_load_state("networkidle")
        self.page.locator("#plone-contentmenu-factories > a").click()
        self.page.wait_for_timeout(500)
        self.shot("add-new-menu", clip={"x": 0, "y": 0, "width": 520, "height": 620})

    def add_form(self):
        self.goto(f"{self.site_url}/++add++EasyForm")
        self.page.get_by_label("Title").first.fill("Contact form")
        self.page.get_by_label("Summary").first.fill(
            "Questions, feedback, requests - we are happy to hear from you."
        )
        self.shot("new-easyform-default")
        self.click_tab("Thanks Page")
        self.shot("new-easyform-thankspage")
        self.click_tab("Overrides")
        self.shot("new-easyform-overrides")
        self.page.get_by_role("button", name="Save").click()
        self.page.wait_for_load_state("networkidle")
        self.shot("created-easyform")

    def fields(self):
        self.goto("@@fields")
        self.shot("created-easyform-fields")

        modal = self.add_in_modal(
            "#add-field", "Phone", "Text line (String)", "Field type"
        )
        self.shot("add-new-field-overlay")
        self.submit_modal(modal)
        self.shot("added-new-field")

        self.settings_link("phone").click()
        modal = self.modal()
        self.shot("field-settings")
        modal.get_by_role("link", name="Advanced").first.click()
        self.page.wait_for_timeout(300)
        self.shot("field-settings-advanced")
        self.close_modal()

        self.page.locator("#add-fieldset").click()
        modal = self.modal()
        modal.get_by_label("Title").fill("Your address")
        self.shot("add-new-fieldset-overlay")
        self.close_modal()

        self.goto("@@modeleditor")
        self.shot("edit-xml-fields-model-page")

    def actions(self):
        self.goto("@@actions")
        self.shot("created-easyform-actions")

        modal = self.add_in_modal(
            "a[href$='@@add-action']", "Save data", "Save Data", "Action type"
        )
        self.shot("add-new-action-overlay")
        self.submit_modal(modal)
        self.shot("added-new-action")

        self.settings_link("mailer").click()
        modal = self.modal()
        modal.get_by_label("Recipient's full name").fill("Front office")
        modal.get_by_label("Recipient's e-mail address").fill("office@example.org")
        self.shot("mailer-settings")
        modal.get_by_role("link", name="Message").first.click()
        self.page.wait_for_timeout(300)
        self.shot("mailer-adapter-message-settings")
        self.submit_modal(modal, button="Save")

        self.goto("actions/@@modeleditor")
        self.shot("edit-xml-actions-model-page")

    def submit_form(self):
        # the demo site has no mail setup: switch the mailer off, so the
        # submission only exercises the save data action
        self.goto("@@actions")
        self.page.get_by_role("checkbox", name="Mailer").uncheck()
        self.page.get_by_role("button", name="Save").click()
        self.page.wait_for_load_state("networkidle")

        self.goto(self.form_url)
        self.page.get_by_label("Your E-Mail Address").fill("jane@example.org")
        self.page.get_by_label("Subject").fill("Opening hours")
        self.page.get_by_label("Phone").fill("+43 1 234 56 78")
        self.page.get_by_label("Comments").fill(
            "Hello,\n\nare you open on Saturdays?\n\nKind regards, Jane"
        )
        self.shot("form-filled")
        self.page.get_by_role("button", name="Submit").click()
        self.page.wait_for_load_state("networkidle")
        self.shot("thanks-page")

        self.goto("actions/save_data/@@data")
        self.shot("saved-data")

    def double_opt_in(self):
        self.goto("@@actions")
        self.page.locator("a[href$='@@add-action']").first.click()
        modal = self.modal()
        options = (
            modal.get_by_label("Action type").locator("option").all_text_contents()
        )
        self.close_modal()
        if "Double Opt-In" not in options:
            print("  skipped: this collective.easyform has no Double Opt-In action")
            return
        modal = self.add_in_modal(
            "a[href$='@@add-action']", "Double opt-in", "Double Opt-In", "Action type"
        )
        self.submit_modal(modal)

        self.settings_link("double_opt_in").click()
        modal = self.modal()
        modal.get_by_label("E-mail field").select_option(label="Your E-Mail Address")
        self.shot("doubleoptin-settings")
        self.close_modal()

        self.goto("@@doubleoptin-pending")
        self.shot("doubleoptin-pending")


def main():
    args = parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel=args.channel or None, headless=not args.headed
        )
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        shooter = Shooter(page, args.url, args.out)
        shooter.login(args.user, args.password)
        shooter.remove_demo_form()
        for step in (
            shooter.add_new_menu,
            shooter.add_form,
            shooter.fields,
            shooter.actions,
            shooter.submit_form,
            shooter.double_opt_in,
        ):
            print(step.__name__)
            step()
        shooter.remove_demo_form()
        browser.close()


if __name__ == "__main__":
    main()
