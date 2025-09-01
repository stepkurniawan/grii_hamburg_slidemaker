"""
This file consist the logic for the new annoucement: 
Take image from the announcement drive https://drive.google.com/drive/u/0/folders/1VdvaMjeAA0HsMpGmQ5OVsjKanarjaukU
check if it's an image, copy it and create paste it in a new slide
"""

from typing import Dict, List
from Pujian import save_images_from_google_folder_to_memory
from pptx_creator import make_slides_from_imgs
from settings import Settings

settings = Settings()


def insert_annoucement_slides(prs):
    images_dict: Dict[str, bytes] = save_images_from_google_folder_to_memory(settings.ANNOUCEMENT_FOLDER_ID)
    images: List[bytes] = list(images_dict.values())
    make_slides_from_imgs(prs, images)








