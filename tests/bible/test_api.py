import requests

from grii_slide_maker.bible import api as bible_api
from grii_slide_maker.models import BibleSuperSearchResponse, BibleVerseDict, Passage, Verse


class FakeEsvService:
    def __init__(self, passage):
        self.passage = passage
        self.references = []

    def get_passage(self, reference):
        self.references.append(reference)
        return self.passage


def test_fetch_bible_passage_validates_http_response(
    monkeypatch, fake_http_response, bible_supersearch_payload
):
    calls = []
    fake_http_response.payload = bible_supersearch_payload

    def fake_get(url, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return fake_http_response

    monkeypatch.setattr(bible_api.requests, "get", fake_get)

    response = bible_api.fetch_bible_passage("indo_tb", "Genesis 1:1-2")

    assert isinstance(response, BibleSuperSearchResponse)
    assert calls == [
        {
            "url": bible_api.BASE_URL,
            "params": {"bible": "indo_tb", "reference": "Genesis 1:1-2"},
            "timeout": bible_api.REQUEST_TIMEOUT_SECONDS,
        }
    ]


def test_fetch_bible_passage_wraps_network_errors(monkeypatch):
    def fake_get(url, params, timeout):
        raise requests.ConnectionError("DNS failed")

    monkeypatch.setattr(bible_api.requests, "get", fake_get)

    try:
        bible_api.fetch_bible_passage("indo_tb", "Romans 12:17-21")
    except bible_api.BiblePassageFetchError as error:
        assert "Could not fetch Bible passage from BibleSuperSearch" in str(error)
        assert "Romans 12:17-21" in str(error)
        assert "indo_tb" in str(error)
    else:
        raise AssertionError("Expected network errors to raise BiblePassageFetchError")


def test_get_verses_dict_combines_local_language_and_esv(
    monkeypatch, bible_supersearch_payload
):
    esv_service = FakeEsvService(
        Passage(
            reference="Genesis 1:1-2",
            verses=[
                Verse(chapter=1, number=1, text="In the beginning"),
                Verse(chapter=1, number=2, text="The earth was without form"),
            ],
        )
    )

    monkeypatch.setattr(
        bible_api,
        "fetch_bible_passage",
        lambda bible_version, reference: BibleSuperSearchResponse.model_validate(
            bible_supersearch_payload
        ),
    )
    monkeypatch.setattr(bible_api, "get_esv_service", lambda: esv_service)

    verses = bible_api.get_verses_dict("Genesis", "1", "1", "2", "ID")

    assert isinstance(verses, BibleVerseDict)
    assert verses.as_dict() == {
        "Kejadian 1:1": "Pada mulanya...",
        "Kejadian 1:2": "Bumi belum berbentuk...",
        "Genesis 1:1": "In the beginning",
        "Genesis 1:2": "The earth was without form",
    }
    assert esv_service.references == ["Genesis 1:1-2"]


def test_get_verses_dict_english_uses_esv_without_bible_supersearch(monkeypatch):
    esv_service = FakeEsvService(
        Passage(
            reference="Genesis 1:1-2",
            verses=[
                Verse(chapter=1, number=1, text="In the beginning"),
                Verse(chapter=1, number=2, text="The earth was without form"),
            ],
        )
    )

    def fail_fetch(bible_version, reference):
        raise AssertionError("BibleSuperSearch should not be called for EN verses")

    monkeypatch.setattr(bible_api, "fetch_bible_passage", fail_fetch)
    monkeypatch.setattr(bible_api, "get_esv_service", lambda: esv_service)

    verses = bible_api.get_verses_dict("Genesis", "1", "1", "2", "EN")

    assert verses.as_dict() == {
        "Genesis 1:1": "In the beginning",
        "Genesis 1:2": "The earth was without form",
    }
    assert esv_service.references == ["Genesis 1:1-2"]


def test_get_verses_dict_rejects_unsupported_language():
    try:
        bible_api.get_verses_dict("Genesis", "1", "1", "2", "FR")
    except ValueError as error:
        assert str(error) == "Unsupported Bible language: FR"
    else:
        raise AssertionError("Expected unsupported language to raise ValueError")
