"""Shared service factories for application-wide dependencies."""

from functools import lru_cache

from grii_slide_maker.config import get_settings
from grii_slide_maker.services.esv_service import EsvService


@lru_cache
def get_esv_service() -> EsvService:
    """Return the shared ESV API service instance."""
    return EsvService(settings=get_settings())
