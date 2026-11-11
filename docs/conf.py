# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "zgw-apis-client"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
]

exclude_patterns = ["_build"]
html_theme = "sphinx_rtd_theme"
root_doc = "index"
