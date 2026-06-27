from grii_slide_maker.bible.translations import (
    english_to_german_bible,
    english_to_indonesian_bible,
    indonesian_to_english_bible,
    indonesian_to_german_bible,
    lai_abbre_to_full,
)


def test_translation_maps_cover_common_service_books():
    assert indonesian_to_english_bible["Kejadian"] == "Genesis"
    assert english_to_indonesian_bible["Genesis"] == "Kejadian"
    assert indonesian_to_german_bible["Mazmur"] == "Psalmen"
    assert english_to_german_bible["John"] == "Johannes"
    assert lai_abbre_to_full["Mzm"] == "Mazmur"


def test_english_to_indonesian_is_reverse_of_indonesian_to_english():
    for indonesian_name, english_name in indonesian_to_english_bible.items():
        assert english_to_indonesian_bible[english_name] == indonesian_name
