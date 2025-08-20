from pydantic import BaseSettings, Field

class Settings (BaseSettings):
    """Settings for the application."""
    # General settings
    app_name: str = Field("My Application", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")

    # Database settings
    ESV_API_KEY : str
    ESV_TEXT_API_URL = 'https://api.esv.org/v3/passage/text/'
    ESV_HTML_API_URL = 'https://api.esv.org/v3/passage/html/'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"