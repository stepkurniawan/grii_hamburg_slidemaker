from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl

class Settings (BaseSettings):
    """Settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".streamlit/secrets.toml",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General settings
    app_name: str = Field("SlideMaker", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")

    # Database settings
    ESV_BIBLE_API_KEY : str
    ESV_TEXT_API_URL: HttpUrl = HttpUrl('https://api.esv.org/v3/passage/text/')
    ESV_HTML_API_URL: HttpUrl = HttpUrl('https://api.esv.org/v3/passage/html/')

    ANNOUCEMENT_FOLDER_ID: str = Field("1VdvaMjeAA0HsMpGmQ5OVsjKanarjaukU")

