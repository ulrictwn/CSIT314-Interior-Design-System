"""Small HTML form reader shared by Sprint 1's form checks."""
from html.parser import HTMLParser

import pytest


class FormControls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.controls = []

    def handle_starttag(self, tag, attrs):
        if tag in ('input', 'textarea', 'select'):
            self.controls.append(dict(attrs))


@pytest.fixture
def form_controls():
    def read(html):
        parser = FormControls()
        parser.feed(html)
        return parser.controls
    return read
