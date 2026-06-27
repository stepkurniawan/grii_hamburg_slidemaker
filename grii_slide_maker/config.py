from typing import ClassVar

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from grii_slide_maker.version import get_app_version


class Settings(BaseSettings):
    """Settings for the application."""

    # ClassVar[str] it’s a normal class constant, not pydantic
    PACKAGE_NAME: ClassVar[str] = "grii-europe-slide-maker"
    DEFAULT_VERSION: ClassVar[str] = "0.0.0"

    model_config = SettingsConfigDict(
        env_file=".streamlit/secrets.toml",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General settings
    app_name: str = "SlideMaker"
    app_version: str = Field(default_factory=get_app_version)

    # Database settings
    ESV_BIBLE_API_KEY: str
    ESV_TEXT_API_URL: HttpUrl = "https://api.esv.org/v3/passage/text/"
    ESV_HTML_API_URL: HttpUrl = "https://api.esv.org/v3/passage/html/"

    GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID: str
    ANNOUCEMENT_FOLDER_ID: str
    GOOGLE_DRIVE_OUTPUT_FOLDER_ID: str
