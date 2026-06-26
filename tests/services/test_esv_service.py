from types import SimpleNamespace

from grii_slide_maker.services.esv_service import EsvService


def make_service(fake_http_session):
    service = EsvService.__new__(EsvService)
    service.settings = SimpleNamespace(ESV_TEXT_API_URL="https://example.test/passage")
    service.http_session = fake_http_session
    return service


def test_get_passage_uses_session_and_returns_parsed_passage(fake_http_session, fake_http_response):
    service = make_service(fake_http_session)

    passage = service.get_passage("Genesis 1:1-2", include_headings=True)

    assert fake_http_response.raise_for_status_called is True
    assert fake_http_session.calls == [
        {
            "url": "https://example.test/passage",
            "params": {
                "q": "Genesis 1:1-2",
                "include_verse_numbers": "true",
                "include_verse_anchors": "false",
                "include_headings": "true",
                "include_subheadings": "false",
                "include_footnotes": "false",
                "include_footnote_body": "false",
                "include_copyright": "false",
                "include_short_copyright": "false",
            },
            "timeout": 30,
        }
    ]
    assert passage.reference == "Genesis 1:1-2"
    assert [verse.number for verse in passage.verses] == [1, 2]
    assert passage.verses[0].heading == "Creation"
    assert passage.verses[1].heading is None
    assert passage.options["include_headings"] is True


def test_parse_passage_without_title_still_extracts_verses(fake_http_session):
    service = make_service(fake_http_session)

    verses = service._parse_passage_verse_text(
        "Psalm 23\n\n[1] The Lord is my shepherd\n\n[2] I shall not want"
    )

    assert [(verse.chapter, verse.number, verse.text) for verse in verses] == [
        (23, 1, "The Lord is my shepherd"),
        (23, 2, "I shall not want"),
    ]
    assert all(verse.heading is None for verse in verses)
