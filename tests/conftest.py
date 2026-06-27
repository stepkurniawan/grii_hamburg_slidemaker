from io import BytesIO
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def test_settings_env(monkeypatch):
    monkeypatch.setenv("ESV_BIBLE_API_KEY", "test-token")
    monkeypatch.setenv("GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID", "song-master-folder")
    monkeypatch.setenv("ANNOUCEMENT_FOLDER_ID", "announcement-folder")
    monkeypatch.setenv("GOOGLE_DRIVE_OUTPUT_FOLDER_ID", "output-folder")


@pytest.fixture
def drive_folder_payload():
    return {
        "id": "folder-1",
        "name": "161",
        "mimeType": "application/vnd.google-apps.folder",
    }


@pytest.fixture
def drive_image_payload():
    return {"id": "image-1", "name": "Slide1.JPG", "mimeType": "image/jpeg"}


@pytest.fixture
def bible_supersearch_payload():
    return {
        "hash": "abc",
        "errors": [],
        "error_level": 0,
        "results": [
            {
                "book_id": 1,
                "book_name": "Genesis",
                "book_short": "Gen",
                "chapter_verse": "1:1 - 2",
                "verses_count": 2,
                "single_verse": False,
                "verses": {
                    "indo_tb": {
                        "1": {
                            "1": {
                                "id": 1,
                                "book": 1,
                                "chapter": 1,
                                "verse": 1,
                                "text": "Pada mulanya...",
                            },
                            "2": {
                                "id": 2,
                                "book": 1,
                                "chapter": 1,
                                "verse": 2,
                                "text": "Bumi belum berbentuk...",
                            },
                        }
                    }
                },
            }
        ],
    }


class FakeHttpResponse:
    def __init__(self, payload):
        self.payload = payload
        self.raise_for_status_called = False

    def raise_for_status(self):
        self.raise_for_status_called = True

    def json(self):
        return self.payload


class FakeHttpSession:
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.response


@pytest.fixture
def fake_http_response():
    return FakeHttpResponse(
        {
            "query": "Genesis 1:1-2",
            "canonical": "Genesis 1:1-2",
            "passages": [
                "Genesis 1:1-2\n\nCreation\n\n[1] In the beginning\n\n[2] The earth was without form"
            ],
        }
    )


@pytest.fixture
def fake_http_session(fake_http_response):
    return FakeHttpSession(fake_http_response)


class FakeShapes:
    def __init__(self):
        self.pictures = []

    def add_picture(self, image, left, top, height, width):
        self.pictures.append(
            {
                "image": image,
                "left": left,
                "top": top,
                "height": height,
                "width": width,
            }
        )


class FakePlaceholder:
    def __init__(self, idx=None):
        self.text = ""
        self.is_placeholder = True
        self.placeholder_format = SimpleNamespace(idx=idx, type="BODY")


class FakeSlide:
    def __init__(self, layout=None):
        self.layout = layout
        self.shapes = FakeShapes()
        self.placeholders = {10: FakePlaceholder(10), 11: FakePlaceholder(11)}


class FakeSlides:
    def __init__(self):
        self.added = []

    def add_slide(self, layout):
        slide = FakeSlide(layout)
        self.added.append(slide)
        return slide


class FakePresentation:
    def __init__(self, layout_names=None):
        layouts = [SimpleNamespace(name=name) for name in (layout_names or ["Blank"])]
        self.slide_master = SimpleNamespace(slide_layouts=layouts)
        self.slide_layouts = layouts
        self.slides = FakeSlides()
        self.slide_height = 900
        self.slide_width = 1600


@pytest.fixture
def fake_prs():
    return FakePresentation(
        [
            "Title",
            "COVER_2",
            "BIBLE_READING",
            "BIBLE_VERSE",
            "Section",
            "Comparison",
            "Blank",
        ]
    )


@pytest.fixture
def image_bytes():
    return BytesIO(b"image-bytes")
