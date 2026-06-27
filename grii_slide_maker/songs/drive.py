"""Song slide lookup helpers backed by Google Drive."""

import os
import sys

import streamlit as st

from grii_slide_maker.config import Settings
from grii_slide_maker.models import DriveFolder
from grii_slide_maker.services.google_drive import (
    get_folder_id_by_name,
    get_list_folders,
    save_images_from_google_folder_to_memory,
)

base_path = getattr(
    sys,
    "_MEIPASS",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

SONGS_FOLDER = os.path.join(base_path, "songs")

settings = Settings()


def st_print(text):
    st.write(text)
    print(text)


def select_song_image_folder(song_number, song_image_folders):
    """Prefer the nested folder matching the song number, then fall back to the first."""
    for folder in song_image_folders:
        drive_folder = DriveFolder.model_validate(folder)
        if drive_folder.name == song_number:
            return folder

    if song_image_folders:
        return song_image_folders[0]

    return None


def folder_english_way(song_number, folder_song_name_list):
    return select_song_image_folder(song_number, folder_song_name_list)


def _raise_song_folder_not_found(song_number):
    message = (
        "Folder_song_name_inside is not found, I cannot find the song number "
        f"in the Master Folder: {song_number}"
    )
    st_print("Folder inside is not found, song_name:" + str(song_number))
    st.error(message)
    raise IndexError(message)


def download_new_song_pipeline(song_number):
    song_number = str(song_number)
    st_print("Downloading song number: " + song_number)
    master_lagu_ibadah_folder_id = settings.GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID

    song_folder_id = get_folder_id_by_name(song_number, master_lagu_ibadah_folder_id)
    if song_folder_id is None:
        _raise_song_folder_not_found(song_number)

    song_image_folders = get_list_folders(song_folder_id)
    print(song_image_folders)
    if song_image_folders is None:
        _raise_song_folder_not_found(song_number)

    selected_folder = select_song_image_folder(song_number, song_image_folders)
    if selected_folder is None:
        st.error(
            "English folder not found, please check google drive path to make "
            "sure this is intended, song: " + song_number
        )
        return None

    st_print("Downloading from google drive song number: " + song_number)
    song_folder = DriveFolder.model_validate(selected_folder)
    return save_images_from_google_folder_to_memory(song_folder.id)

