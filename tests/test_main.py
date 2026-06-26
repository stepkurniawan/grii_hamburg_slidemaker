import datetime


class FixedDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2026, 6, 26)


def test_sunday_date_returns_next_sunday_formats(monkeypatch):
    import main

    monkeypatch.setattr(main.datetime, "date", FixedDate)

    assert main.sunday_date("filename") == "20260628"
    assert main.sunday_date("slide") == "28 June 2026"
    assert main.sunday_date("date") == datetime.date(2026, 6, 28)


def test_processing_answers_adapts_legacy_form_data():
    import main

    order = main.processing_answers(
        ["161, 320, 93, 169", "Pdt. Billy Kristanto", "Genesis 1:2-3", "Rev.", ""]
    )

    assert [song.value for song in order.songs.worship_songs] == [
        "161",
        "320",
        "93",
        "169",
    ]
    assert order.pastor.name == "Billy Kristanto"
    assert [reference.as_reference_text() for reference in order.bible_references] == [
        "Genesis 1:2-3"
    ]
