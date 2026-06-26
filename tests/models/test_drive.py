from io import BytesIO

import pytest
from pydantic import ValidationError

from grii_slide_maker.models import DriveFolder, DriveImageFile, DriveItem, SongImageSet


def test_drive_folder_validates_folder_payload():
    folder = DriveFolder.model_validate(
        {
            "id": "folder-id",
            "name": "161",
            "mimeType": "application/vnd.google-apps.folder",
        }
    )

    assert folder.is_folder


def test_drive_folder_can_validate_from_drive_item():
    item = DriveItem.model_validate(
        {
            "id": "folder-id",
            "name": "161",
            "mimeType": "application/vnd.google-apps.folder",
        }
    )

    folder = DriveFolder.model_validate(item)

    assert folder.id == "folder-id"


def test_drive_image_file_rejects_non_image_payload():
    with pytest.raises(ValidationError):
        DriveImageFile.model_validate(
            {
                "id": "file-id",
                "name": "notes.txt",
                "mimeType": "text/plain",
            }
        )


def test_song_image_set_requires_bytesio_images():
    image_set = SongImageSet.model_validate({"images": {"Slide1.JPG": BytesIO(b"image")}})

    assert list(image_set.images) == ["Slide1.JPG"]
