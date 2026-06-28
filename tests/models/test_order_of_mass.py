import pytest
from pydantic import ValidationError

from grii_slide_maker.models import Pastor, OrderOfMass, SongSelection


def test_song_selection_accepts_four_trimmed_songs():
    selection = SongSelection.model_validate("161, 320, 93, 169")

    assert [song.value for song in selection.worship_songs] == ["161", "320", "93", "169"]


def test_song_selection_parses_holy_communion_song_from_song_list():
    selection = SongSelection.model_validate("236, 299, 199, 22, HC 264")

    assert [song.value for song in selection.worship_songs] == ["236", "299", "199", "22"]
    assert selection.holy_communion_song.value == "264"


@pytest.mark.parametrize("song_numbers", ["161, 320, 93", "161, 320, 93, 169, 200"])
def test_song_selection_rejects_wrong_song_count(song_numbers):
    with pytest.raises(ValidationError):
        SongSelection.model_validate(song_numbers)


def test_song_selection_rejects_non_numeric_song_id():
    with pytest.raises(ValidationError):
        SongSelection.model_validate("161, test, 93, 169")


def test_service_order_accepts_optional_holy_communion_song():
    order = OrderOfMass.model_validate(
        {
            "song_numbers": "161, 320, 93, 169",
            "pastor_name": "Pdt. Billy Kristanto",
            "bible_verses": "Genesis 1:2-3",
            "pastor_title": "Rev.",
            "holy_communion_song_number": "94",
        }
    )

    assert order.songs.holy_communion_song.value == "94"


def test_pastor_preserves_multi_word_name():
    pastor = Pastor.model_validate("Pdt. Billy Very Long Name")

    assert pastor.title_id == "Pdt."
    assert pastor.name == "Billy Very Long Name"


@pytest.mark.parametrize("pastor_name", ["", "Pdt."])
def test_pastor_rejects_missing_name(pastor_name):
    with pytest.raises(ValidationError):
        Pastor.model_validate(pastor_name)
