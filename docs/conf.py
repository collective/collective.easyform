# Sphinx configuration for the collective.easyform documentation.
# Built by Read the Docs, see .readthedocs.yaml in the repository root.

project = "collective.easyform"
copyright = "2014-2026, Plone Collective"
author = "Plone Collective"
release = "5.x"

extensions = []
master_doc = "index"
exclude_patterns = ["_build"]

html_theme = "alabaster"
html_theme_options = {
    "description": "Form builder for Plone",
    "github_user": "collective",
    "github_repo": "collective.easyform",
    "github_button": True,
    "page_width": "1100px",
}
html_static_path = []
