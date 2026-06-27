import pytest
from pydantic import ValidationError

from grii_slide_maker.models import (
    BibleReference,
    BibleSuperSearchResponse,
    BibleVerseDict,
    Passage,
    Verse,
)


@pytest.mark.parametrize("reference", ["Genesis 1:2-3", "1 Kings 1:1-2"])
def test_bible_reference_accepts_supported_references(reference):
    bible_reference = BibleReference.model_validate(reference)

    assert bible_reference.as_reference_text() == reference


@pytest.mark.parametrize(
    "reference",
    ["Genesis", "Genesis 1:3-2", "Madeup 1:1-2", "Genesis 1:1"],
)
def test_bible_reference_rejects_invalid_references(reference):
    with pytest.raises(ValidationError):
        BibleReference.model_validate(reference)


def test_bible_supersearch_response_validates_nested_verses():
    response = BibleSuperSearchResponse.model_validate(
        {
            "hash": "abc",
            "errors": [],
            "error_level": 0,
            "results": [
                {
                    "book_id": 1,
                    "book_name": "Genesis",
                    "book_short": "Gen",
                    "chapter_verse": "1:1 - 2",
                    "verses_count": 2,
                    "single_verse": False,
                    "verses": {
                        "indo_tb": {
                            "1": {
                                "1": {
                                    "id": 1,
                                    "book": 1,
                                    "chapter": 1,
                                    "verse": 1,
                                    "text": "Pada mulanya...",
                                }
                            }
                        }
                    },
                }
            ],
        }
    )

    verse = response.results[0].verses["indo_tb"]["1"]["1"]
    assert verse.text == "Pada mulanya..."


def test_bible_verse_dict_validates_and_behaves_like_mapping():
    verses = BibleVerseDict.model_validate(
        {
            "Kejadian 1:1": "Pada mulanya...",
            "Genesis 1:1": "In the beginning",
        }
    )

    assert verses["Genesis 1:1"] == "In the beginning"
    assert list(verses.keys()) == ["Kejadian 1:1", "Genesis 1:1"]
    assert verses.as_dict() == {
        "Kejadian 1:1": "Pada mulanya...",
        "Genesis 1:1": "In the beginning",
    }

    with pytest.raises(ValidationError):
        BibleVerseDict.model_validate({"Genesis 1:1": ""})


def test_esv_passage_requires_at_least_one_verse():
    passage = Passage.model_validate(
        {
            "reference": "Genesis 1:1",
            "verses": [{"chapter": 1, "number": 1, "text": "In the beginning"}],
        }
    )

    assert isinstance(passage.verses[0], Verse)

    with pytest.raises(ValidationError):
        Passage.model_validate({"reference": "Genesis 1:1", "verses": []})
