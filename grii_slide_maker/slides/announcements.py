"""Add announcement images from Google Drive to the slide deck."""

from typing import Dict, List
from grii_slide_maker.config import get_settings
from grii_slide_maker.slides.creator import make_slides_from_imgs
from grii_slide_maker.services.google_drive import save_images_from_google_folder_to_memory

settings = get_settings()


def insert_annoucement_slides(prs: object) -> None:
    images_dict: Dict[str, bytes] = save_images_from_google_folder_to_memory(settings.ANNOUCEMENT_FOLDER_ID)
    images: List[bytes] = list(images_dict.values())
    make_slides_from_imgs(prs, images)
