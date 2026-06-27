"""Filesystem paths used by the Streamlit app and slide generator."""

from io import BytesIO
import os
import sys


CURRENT_DIR = getattr(
    sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PACKAGE_DIR, "output")
binary_output_file = BytesIO()


def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = CURRENT_DIR

    return os.path.join(base_path, relative_path)


TEMPLATE_FILE = get_resource_path("master_slide_template_en.pptx")
