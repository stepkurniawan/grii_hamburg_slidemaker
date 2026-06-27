import pytest

from grii_slide_maker import website


class FakeSidebar:
    def __init__(self, text_values=None, checkbox_value=False):
        self.text_values = list(text_values or [])
        self.checkbox_value = checkbox_value
        self.errors = []
        self.messages = []

    def subheader(self, text):
        self.messages.append(("subheader", text))

    def write(self, text):
        self.messages.append(("write", text))

    def text_input(self, label):
        self.messages.append(("text_input", label))
        if self.text_values:
            return self.text_values.pop(0)
        return ""

    def checkbox(self, label, key=None, help=None):
        self.messages.append(("checkbox", label, key, help))
        return self.checkbox_value

    def error(self, text):
        self.errors.append(text)


@pytest.mark.parametrize(
    ("renderer", "expected"),
    [
        (website.render_song_inputs, ""),
        (website.render_bible_inputs, ""),
        (website.render_pastor_name_input, "Pdt. Billy Kristanto"),
        (website.render_pastor_title_input, "Rev."),
    ],
)
def test_sidebar_input_renderers_return_defaults(monkeypatch, renderer, expected):
    fake_sidebar = FakeSidebar()
    monkeypatch.setattr(website.st, "sidebar", fake_sidebar)

    assert renderer() == expected


@pytest.mark.parametrize(
    ("checked", "text_values", "expected", "expected_errors"),
    [
        (False, [], None, []),
        (True, ["94"], "94", []),
        (True, [""], "", ["Please enter the Holy Communion song number."]),
    ],
)
def test_render_holy_communion_inputs(
    monkeypatch, checked, text_values, expected, expected_errors
):
    fake_sidebar = FakeSidebar(text_values=text_values, checkbox_value=checked)
    monkeypatch.setattr(website.st, "sidebar", fake_sidebar)

    assert website.render_holy_communion_inputs() == expected
    assert fake_sidebar.errors == expected_errors
