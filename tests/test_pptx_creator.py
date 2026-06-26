import datetime
from pathlib import Path

from models import OfferingPurpose


def test_sort_by_number_sorts_embedded_numbers():
    from pptx_creator import sort_by_number

    assert sorted(["Slide10.JPG", "Slide2.JPG", "notes"], key=sort_by_number) == [
        "Slide2.JPG",
        "Slide10.JPG",
        "notes",
    ]


def test_insert_slides_from_pict_folder_adds_only_images(tmp_path, fake_prs):
    from pptx_creator import insert_slides_from_pict_folder

    for name in ["Slide2.JPG", "notes.txt", "Slide1.png"]:
        (tmp_path / name).write_bytes(b"image")

    insert_slides_from_pict_folder(fake_prs, tmp_path)

    added_images = [
        picture["image"]
        for slide in fake_prs.slides.added
        for picture in slide.shapes.pictures
    ]
    assert [Path(path).name for path in added_images] == [
        "Slide1.png",
        "Slide2.JPG",
    ]


def test_add_slide_layout_from_layout_name_uses_matching_layout(fake_prs):
    from pptx_creator import add_slide_layout_from_layout_name

    slide = add_slide_layout_from_layout_name(fake_prs, "COVER_2")

    assert slide.layout.name == "COVER_2"


def test_decide_offering_purpose_layout_name_maps_week_of_month():
    from pptx_creator import decide_offering_purpose_layout_name

    assert decide_offering_purpose_layout_name(datetime.date(2026, 6, 7)) == (
        OfferingPurpose.P_PENGINJILAN
    )
    assert decide_offering_purpose_layout_name(datetime.date(2026, 6, 14)) == (
        OfferingPurpose.P_SEKOLAH
    )
    assert decide_offering_purpose_layout_name(datetime.date(2026, 6, 21)) == (
        OfferingPurpose.P_MANDAT
    )
    assert decide_offering_purpose_layout_name(datetime.date(2026, 6, 28)) == (
        OfferingPurpose.P_PEMBANGUNAN
    )
    assert decide_offering_purpose_layout_name(datetime.date(2026, 6, 29)) == (
        OfferingPurpose.P_DIAKONIA
    )
