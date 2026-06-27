import datetime
from io import BytesIO
import os

from pptx import Presentation

from grii_slide_maker import app as main
from grii_slide_maker import presentation
from grii_slide_maker.models import OrderOfMass


class FixedDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2026, 6, 26)


def test_sunday_date_returns_next_sunday_formats(monkeypatch):
    monkeypatch.setattr(main.datetime, "date", FixedDate)

    assert main.sunday_date("filename") == "20260628"
    assert main.sunday_date("slide") == "28 June 2026"
    assert main.sunday_date("date") == datetime.date(2026, 6, 28)


def test_default_output_dir_is_under_package_dir():
    assert main.OUTPUT_DIR == os.path.join(main.PACKAGE_DIR, "output")


def test_main_outputs_downloadable_and_saved_pptx(tmp_path, monkeypatch):
    service_order = OrderOfMass.model_validate(
        {
            "song_numbers": "161, 320, 93, 169",
            "pastor_name": "Pdt. Billy Kristanto",
            "bible_verses": "Genesis 1:2-3",
            "pastor_title": "Rev.",
            "holy_communion_song_number": None,
        }
    )

    monkeypatch.setattr(main.datetime, "date", FixedDate)
    monkeypatch.setattr(main, "OUTPUT_DIR", str(tmp_path))

    slide_actions = presentation.SlideDeckActions(
        insert_song_slides_drive_folder=lambda prs, song_number: None,
        add_bible_reading_page=lambda prs, bible_verse: None,
        insert_annoucement_slides=lambda prs: None,
    )
    monkeypatch.setattr(presentation, "SlideDeckActions", lambda: slide_actions)

    main.main(service_order)

    download_bytes = main.binary_output_file.getvalue()
    saved_file = tmp_path / "20260628.pptx"

    assert download_bytes.startswith(b"PK")
    assert saved_file.exists()
    assert saved_file.read_bytes() == download_bytes
    assert len(Presentation(BytesIO(download_bytes)).slides) > 0
