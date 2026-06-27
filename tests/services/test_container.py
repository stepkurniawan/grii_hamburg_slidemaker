from grii_slide_maker.config import get_settings
from grii_slide_maker.services.container import get_esv_service


def test_get_settings_returns_cached_instance():
    assert get_settings() is get_settings()


def test_get_esv_service_returns_cached_instance():
    service = get_esv_service()

    assert service is get_esv_service()
    assert service.settings is get_settings()
