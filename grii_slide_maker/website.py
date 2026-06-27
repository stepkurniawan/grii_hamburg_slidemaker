"""Streamlit UI for collecting service details and downloading slides."""

from collections.abc import Callable
from io import BytesIO

import streamlit as st
from pydantic import ValidationError

from grii_slide_maker.config import Settings
from grii_slide_maker.models import OrderOfMass
from grii_slide_maker.songs.drive import SONGS_FOLDER
from grii_slide_maker.slides.footer import footer


def show_validation_errors(error: ValidationError) -> None:
    for validation_error in error.errors():
        location = " > ".join(str(part) for part in validation_error["loc"])
        message = validation_error["msg"]
        st.sidebar.error(f"{location}: {message}")


def create_website(
    *,
    version: str,
    settings: Settings,
    output_dir: str,
    binary_output_file: BytesIO,
    generate_slide: Callable[[OrderOfMass], None],
    sunday_date: Callable[[str], object],
) -> None:
    page_title = "☁️ MRII Europe SlideMaker"

    st.set_page_config(page_icon=":church:", page_title=page_title)

    st.title(page_title)
    st.subheader(" 📜 Welcome to MRII Europe SlideMaker V" + version + " A1")
    st.write("This website is used to create a powerpoint presentation for Sunday service.")
    st.write("It is tweaked for Hamburg Church, which is bilingual (English and Indo).")

    st.subheader("How to use this website")
    st.write("1. Enter the song numbers separated by comma on the left sidebar")
    st.write("2. Enter the (English) Bible verse. ex: Genesis 1:2-3, 1 Kings 1:1-2")
    st.write("3. (Optional) Enter the pastor name ")
    st.write("4. (Optional) Enter the pastor title in English ")
    st.write("5. Click the submit button")

    st.subheader("Where are the songs?")
    st.write(
        "The songs are downloaded from the database to the in-memory, since we don't have permission to store it in the server."
    )
    st.write("It is stored in the folder, in the server: " + SONGS_FOLDER)

    st.subheader("Where is the Slide?")
    st.markdown("After the main process is finished, the **Download Button** will appear on the **left sidebar**")
    st.markdown("You can save the slide by clicking on the **Download Button**")
    st.markdown("The file name is the date of the **next Sunday** service")

    song_numbers = render_song_inputs()
    holy_communion_song_number = render_holy_communion_inputs()
    bible_verses = render_bible_inputs()
    pastor_name = render_pastor_name_input()
    pastor_title = render_pastor_title_input()

    submit_button = st.sidebar.button("Submit")
    if submit_button:
        try:
            service_order = OrderOfMass.model_validate(
                {
                    "song_numbers": song_numbers,
                    "pastor_name": pastor_name,
                    "bible_verses": bible_verses,
                    "pastor_title": pastor_title,
                    "holy_communion_song_number": holy_communion_song_number,
                }
            )
        except ValidationError as error:
            st.sidebar.error("Please fix the input before generating the slide.")
            show_validation_errors(error)
            footer()
            return

        st.write("Validated service order")
        st.write(service_order.model_dump(mode="json"))
        with st.spinner("Generating the slide..."):
            generate_slide(service_order)
            st.balloons()
            output_drive_folder_url = "https://drive.google.com/drive/folders/" + settings.GOOGLE_DRIVE_OUTPUT_FOLDER_ID
            st.sidebar.success("Slide generated successfully in " + output_dir + ":tada:" + output_drive_folder_url)

            st.sidebar.download_button(
                label="Download slide!",
                data=binary_output_file.getvalue(),
                file_name=sunday_date("filename") + ".pptx",
            )

    footer()


def render_song_inputs() -> str:
    st.sidebar.subheader("Song numbers")
    st.sidebar.write("Please enter the song numbers separated by comma")
    st.sidebar.write("Example: 161, 320, 93, 169")
    return st.sidebar.text_input("Song numbers")


def render_holy_communion_inputs() -> str | None:
    holy_communion = st.sidebar.checkbox(
        "Holy Communion",
        key="holy_communion",
        help="Toggle this if the service is Holy Communion. This will add the Holy Communion song slide before the sermon.",
    )
    if not holy_communion:
        return None

    st.sidebar.write("Holy Communion song will be added before the sermon slide.")
    holy_communion_song_number = st.sidebar.text_input("Holy Communion song number")
    if not holy_communion_song_number:
        st.sidebar.error("Please enter the Holy Communion song number.")
    return holy_communion_song_number


def render_bible_inputs() -> str:
    st.sidebar.subheader("Bible verse")
    st.sidebar.write("Please enter the Bible verse in English")
    st.sidebar.write("Example: Genesis 1:2-3, 1 Kings 1:1-2")
    return st.sidebar.text_input("Bible verse(s)")


def render_pastor_name_input() -> str:
    st.sidebar.subheader("Pastor name")
    st.sidebar.write("Please enter the pastor name")
    st.sidebar.write("Default Example: Pdt. Billy Kristanto")
    return st.sidebar.text_input("Pastor name") or "Pdt. Billy Kristanto"


def render_pastor_title_input() -> str:
    st.sidebar.subheader("Pastor title")
    st.sidebar.write("Please enter the pastor title")
    st.sidebar.write("Default Example: Rev.")
    return st.sidebar.text_input("Pastor title") or "Rev."
