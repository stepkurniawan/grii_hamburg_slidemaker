from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".streamlit/secrets.toml",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General settings
    app_name: str = "SlideMaker"
    app_version: str = "3.0.0"

    # Database settings
    ESV_BIBLE_API_KEY: str
    ESV_TEXT_API_URL: HttpUrl = "https://api.esv.org/v3/passage/text/"
    ESV_HTML_API_URL: HttpUrl = "https://api.esv.org/v3/passage/html/"

    GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID: str
    ANNOUCEMENT_FOLDER_ID: str
    GOOGLE_DRIVE_OUTPUT_FOLDER_ID: str
