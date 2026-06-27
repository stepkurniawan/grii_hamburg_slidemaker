from grii_slide_maker.config import Settings, get_settings


def test_settings_reads_required_environment_values():
    settings = Settings()

    assert settings.ESV_BIBLE_API_KEY == "test-token"
    assert settings.GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID == "song-master-folder"
    assert settings.ANNOUCEMENT_FOLDER_ID == "announcement-folder"
    assert str(settings.ESV_TEXT_API_URL) == "https://api.esv.org/v3/passage/text/"


def test_get_settings_returns_shared_settings_instance():
    assert get_settings() is get_settings()
