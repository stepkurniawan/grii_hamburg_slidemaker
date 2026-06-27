import pytest
from pydantic import ValidationError

from grii_slide_maker.models.service_order import Pastor, ServiceOrder, SongSelection


def test_service_order_parses_streamlit_form_shape():
    service_order = ServiceOrder.model_validate(
        {
            "song_numbers": "161, 320, 93, 169",
            "pastor_name": "Pdt. Billy Kristanto",
            "bible_verses": "Genesis 1:2-3, John 3:16-17",
            "pastor_title": "Rev.",
            "holy_communion_song_number": "94",
        }
    )

    assert [song.value for song in service_order.songs.worship_songs] == [
        "161",
        "320",
        "93",
        "169",
    ]
    assert service_order.songs.holy_communion_song.value == "94"
    assert service_order.pastor.name == "Billy Kristanto"
    assert [ref.as_reference_text() for ref in service_order.bible_references] == [
        "Genesis 1:2-3",
        "John 3:16-17",
    ]


def test_service_order_uses_default_pastor_title():
    service_order = ServiceOrder.model_validate(
        {
            "song_numbers": "161, 320, 93, 169",
            "pastor_name": "Pdt. Billy Kristanto",
            "bible_verses": "Genesis 1:2-3",
            "pastor_title": "",
        }
    )

    assert service_order.pastor.title_de_or_en == "Rev."


def test_service_order_rejects_bad_song_count():
    with pytest.raises(ValidationError):
        SongSelection.model_validate("161, 320, 93")


def test_pastor_cleans_extra_whitespace():
    pastor = Pastor.model_validate(
        {
            "title_id": " Pdt. ",
            "title_de_or_en": " Rev. ",
            "name": " Billy   Kristanto ",
        }
    )

    assert pastor.title_id == "Pdt."
    assert pastor.title_de_or_en == "Rev."
    assert pastor.name == "Billy Kristanto"
