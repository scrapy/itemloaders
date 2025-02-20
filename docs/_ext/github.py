from __future__ import annotations

from docutils import nodes
from docutils.parsers.rst.roles import set_classes


def setup(app):
    app.add_role("gh", github_role)


def github_role(
    name,
    rawtext,
    text,
    lineno,
    inliner,
    options: dict[str, str] | None = None,
    content=None,
):
    options = options or {}
    if text.isdigit():
        display_text = f"#{text}"
        url = f"https://github.com/scrapy/itemloaders/issues/{text}"
    else:
        short_commit = text[:7]
        display_text = short_commit
        url = f"https://github.com/scrapy/itemloaders/commit/{short_commit}"

    set_classes(options)
    node = nodes.reference(rawtext, display_text, refuri=url, **options)
    return [node], []
