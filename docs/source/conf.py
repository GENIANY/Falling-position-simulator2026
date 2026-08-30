# Configuration file for the Sphinx documentation builder.
#
# Falling-position-simulator ドキュメント

project = "Falling-position-simulator"
copyright = "2026, Falling-position-simulator contributors"
author = "Falling-position-simulator contributors"

extensions = [
    "sphinxcontrib.mermaid",
    "myst_parser",
]

language = "ja"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

mermaid_output_format = "raw"
