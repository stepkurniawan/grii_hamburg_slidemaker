from functools import lru_cache
from pathlib import Path
from typing import ClassVar

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from grii_slide_maker.version import get_app_version


SECRETS_FILE = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"


class Settings(BaseSettings):
    """Settings for the application."""

    # ClassVar[str] it’s a normal class constant, not pydantic
    PACKAGE_NAME: ClassVar[str] = "grii-europe-slide-maker"
    DEFAULT_VERSION: ClassVar[str] = "0.0.0"

    model_config = SettingsConfigDict(
        env_file=SECRETS_FILE,
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
    GOOGLE_SHEET_MASTER_WARTA_ID: str | None = None

    # Automation workbook settings
    AUTOMATION_SCHEDULE_SHEET_NAME: str = "info"
    AUTOMATION_SERVICE_SHEET_NAME: str = "dashboard"
    AUTOMATION_CRON_DAY_CELL: str = "B2"
    AUTOMATION_CRON_HOUR_CELL: str = "B3"
    AUTOMATION_CRON_MINUTE_CELL: str = "B4"
    AUTOMATION_ENABLED_CELL: str = "B1"
    AUTOMATION_SONG_NUMBERS_LABEL: str = "Songs"
    AUTOMATION_BIBLE_VERSES_LABEL: str = "Bible Reading"
    AUTOMATION_PASTOR_NAME_LABEL: str = "Preacher"
    AUTOMATION_HOLY_COMMUNION_SONG_LABEL: str = "Holy Communion"
    AUTOMATION_DASHBOARD_SECTION_LABEL: str = "THIS WEEK"


@lru_cache
def get_settings() -> Settings:
    """Return the shared application settings instance."""
    return Settings()
