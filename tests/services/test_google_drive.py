from grii_slide_maker.services import google_drive


class FakeDownload:
    def __init__(self, fh, request):
        self.fh = fh
        self.request = request
        self.done = False

    def next_chunk(self):
        self.fh.write(self.request.content)
        self.done = True
        return None, self.done


class FakeMediaRequest:
    def __init__(self, content):
        self.content = content


class FakeFilesResource:
    def __init__(self, list_responses=None, media=None):
        self.list_responses = list(list_responses or [])
        self.media = media or {}
        self.list_calls = []
        self.media_calls = []

    def list(self, **kwargs):
        self.list_calls.append(kwargs)
        return self

    def get_media(self, fileId):
        self.media_calls.append(fileId)
        return FakeMediaRequest(self.media[fileId])

    def execute(self):
        return self.list_responses.pop(0)


class FakeDriveService:
    def __init__(self, files_resource):
        self.files_resource = files_resource

    def files(self):
        return self.files_resource


def test_get_list_folders_returns_all_pages(monkeypatch, drive_folder_payload):
    second_folder = {**drive_folder_payload, "id": "folder-2", "name": "262"}
    files_resource = FakeFilesResource(
        [
            {"nextPageToken": "next", "files": [drive_folder_payload]},
            {"files": [second_folder]},
        ]
    )
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )

    folders = google_drive.get_list_folders("parent-folder")

    assert [folder.id for folder in folders] == ["folder-1", "folder-2"]
    assert files_resource.list_calls[1]["pageToken"] == "next"


def test_get_folder_id_by_name_returns_first_matching_folder(
    monkeypatch, drive_folder_payload
):
    files_resource = FakeFilesResource([{"files": [drive_folder_payload]}])
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )

    folder_id = google_drive.get_folder_id_by_name("161", "parent-folder")

    assert folder_id == "folder-1"


def test_save_images_from_google_folder_to_memory_filters_and_sorts_images(
    monkeypatch,
):
    files_resource = FakeFilesResource(
        [
            {
                "files": [
                    {"id": "image-10", "name": "Slide10.JPG", "mimeType": "image/jpeg"},
                    {"id": "notes", "name": "notes.txt", "mimeType": "text/plain"},
                    {"id": "image-2", "name": "Slide2.JPG", "mimeType": "image/jpeg"},
                ]
            }
        ],
        media={"image-10": b"image-10", "image-2": b"image-2"},
    )
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )
    monkeypatch.setattr(google_drive, "MediaIoBaseDownload", FakeDownload)

    images = google_drive.save_images_from_google_folder_to_memory("folder-1")

    assert list(images) == ["Slide2.JPG", "Slide10.JPG"]
    assert images["Slide2.JPG"].getvalue() == b"image-2"
    assert files_resource.media_calls == ["image-10", "image-2"]
