from grii_slide_maker.slides import footer as footer_module


def test_layout_renders_style_and_footer_html(monkeypatch):
    rendered = []
    monkeypatch.setattr(
        footer_module.st,
        "markdown",
        lambda html, unsafe_allow_html: rendered.append(
            {"html": html, "unsafe": unsafe_allow_html}
        ),
    )

    footer_module.layout("hello")

    assert len(rendered) == 2
    assert all(call["unsafe"] is True for call in rendered)
    assert "# MainMenu" in rendered[0]["html"]
    assert "hello" in rendered[1]["html"]


def test_footer_includes_author_link(monkeypatch):
    rendered = []
    monkeypatch.setattr(
        footer_module.st,
        "markdown",
        lambda html, unsafe_allow_html: rendered.append(html),
    )

    footer_module.footer()

    assert "Stephen Kurniawan" in rendered[-1]
    assert "linkedin.com/in/stepkurniawan" in rendered[-1]
