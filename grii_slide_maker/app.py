"""Build bilingual Sunday service PowerPoint slides for GRII Hamburg."""

import datetime

import streamlit as st
from pptx.util import Inches

from grii_slide_maker.config import get_settings
from grii_slide_maker.dates import sunday_date as format_sunday_date
from grii_slide_maker.models import OrderOfMass
from grii_slide_maker.paths import (
    CURRENT_DIR,
    OUTPUT_DIR,
    PACKAGE_DIR,
    TEMPLATE_FILE,
    binary_output_file,
    get_resource_path,
)
from grii_slide_maker.presentation import build_service_slides
from grii_slide_maker.version import get_app_version
from grii_slide_maker.website import create_website as render_website
from grii_slide_maker.website import show_validation_errors


__all__ = [
    "CURRENT_DIR",
    "OUTPUT_DIR",
    "PACKAGE_DIR",
    "TEMPLATE_FILE",
    "VERSION",
    "binary_output_file",
    "create_website",
    "get_resource_path",
    "main",
    "show_validation_errors",
    "sunday_date",
]


VERSION = get_app_version()

SONG_NUMBERS = ["1", "test", "test", "test"]
OPEN_BIBLE_FULL_VERSES = ["Genesis 1:2-3", "1 Kings 1:1-2"]
OPEN_BIBLE_FULL_VERSE = "Genesis 1:2-3"
PASTOR_TITLE_ID = "Pdt."
PASTOR_TITLE_DE_OR_EN = "Rev."
PASTOR_NAME = "Billy Kristanto"
SECOND_OFFERING_PURPOSE_ID = [
    "NONE",
    "P_PENGINJILAN",
    "P_SEKOLAH",
    "P_MANDAT",
    "P_PEMBANGUNAN",
    "P_DIAKONIA",
]
SELECTED_SECOND_OFFERING_PURPOSE_ID = "NONE"

MY_SLIDE_WIDTH = Inches(16)
MY_SIDE_HEIGHT = Inches(9)
output_file = ""


def st_print(text: str) -> None:
    st.write(text)
    print(text)


def st_error_print(text: str) -> None:
    st.error(text)
    print(text)


def sunday_date(formatted: str) -> str | datetime.date:
    return format_sunday_date(formatted, today=datetime.date.today())


def create_website() -> None:
    render_website(
        version=VERSION,
        settings=get_settings(),
        output_dir=OUTPUT_DIR,
        binary_output_file=binary_output_file,
        generate_slide=main,
        sunday_date=sunday_date,
    )


def main(service_order: OrderOfMass | None = None) -> None:
    build_service_slides(
        service_order,
        template_file=TEMPLATE_FILE,
        output_dir=OUTPUT_DIR,
        binary_output_file=binary_output_file,
        sunday_date=sunday_date,
        status_writer=st_print,
        error_writer=st_error_print,
    )


if __name__ == "__main__":
    create_website()
