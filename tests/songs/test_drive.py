from io import BytesIO

from grii_slide_maker.songs import drive as songs
from grii_slide_maker.songs.drive import select_song_image_folder


def test_select_song_image_folder_prefers_exact_song_folder(drive_folder_payload):
    fallback = {**drive_folder_payload, "id": "folder-2", "name": "fallback"}

    selected = select_song_image_folder("161", [fallback, drive_folder_payload])

    assert selected == drive_folder_payload


def test_select_song_image_folder_falls_back_to_first_folder(drive_folder_payload):
    selected = select_song_image_folder("999", [drive_folder_payload])

    assert selected == drive_folder_payload


def test_download_new_song_pipeline_uses_selected_drive_folder(
    monkeypatch, drive_folder_payload
):
    calls = []
    images = {"Slide1.JPG": BytesIO(b"image")}

    monkeypatch.setattr(songs, "st_print", lambda text: calls.append(("print", text)))
    monkeypatch.setattr(
        songs,
        "get_list_folders",
        lambda folder_id: [drive_folder_payload],
    )
    monkeypatch.setattr(
        songs,
        "get_folder_id_by_name",
        lambda song_number, parent_folder_id: "song-folder",
    )
    monkeypatch.setattr(
        songs,
        "save_images_from_google_folder_to_memory",
        lambda folder_id: images,
    )

    assert songs.download_new_song_pipeline("161") == images
    assert ("print", "Downloading song number: 161") in calls
