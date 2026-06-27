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
    def __init__(
        self,
        list_responses=None,
        media=None,
        metadata=None,
        create_response=None,
        update_response=None,
    ):
        self.list_responses = list(list_responses or [])
        self.media = media or {}
        self.metadata = metadata or {}
        self.create_response = create_response or {"id": "created-file"}
        self.update_response = update_response or {"id": "updated-file"}
        self.list_calls = []
        self.media_calls = []
        self.get_calls = []
        self.export_calls = []
        self.create_calls = []
        self.update_calls = []
        self.current_response = None

    def list(self, **kwargs):
        self.list_calls.append(kwargs)
        self.current_response = self.list_responses.pop(0)
        return self

    def get(self, fileId, fields):
        self.get_calls.append({"fileId": fileId, "fields": fields})
        self.current_response = self.metadata[fileId]
        return self

    def get_media(self, fileId):
        self.media_calls.append(fileId)
        return FakeMediaRequest(self.media[fileId])

    def export_media(self, fileId, mimeType):
        self.export_calls.append({"fileId": fileId, "mimeType": mimeType})
        return FakeMediaRequest(self.media[fileId])

    def create(self, body, media_body, fields):
        self.create_calls.append(
            {"body": body, "media_body": media_body, "fields": fields}
        )
        self.current_response = self.create_response
        return self

    def update(self, fileId, media_body, fields):
        self.update_calls.append(
            {"fileId": fileId, "media_body": media_body, "fields": fields}
        )
        self.current_response = self.update_response
        return self

    def execute(self):
        return self.current_response


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


def test_download_excel_file_to_memory_downloads_xlsx(monkeypatch):
    files_resource = FakeFilesResource(
        media={"excel-file": b"excel-bytes"},
        metadata={
            "excel-file": {
                "id": "excel-file",
                "name": "automation.xlsx",
                "mimeType": google_drive.EXCEL_MIME_TYPE,
            }
        },
    )
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )
    monkeypatch.setattr(google_drive, "MediaIoBaseDownload", FakeDownload)

    excel_file = google_drive.download_excel_file_to_memory("excel-file")

    assert excel_file.getvalue() == b"excel-bytes"
    assert files_resource.media_calls == ["excel-file"]
    assert files_resource.export_calls == []


def test_download_excel_file_to_memory_exports_google_sheet(monkeypatch):
    files_resource = FakeFilesResource(
        media={"sheet-file": b"excel-bytes"},
        metadata={
            "sheet-file": {
                "id": "sheet-file",
                "name": "automation",
                "mimeType": google_drive.GOOGLE_SHEETS_MIME_TYPE,
            }
        },
    )
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )
    monkeypatch.setattr(google_drive, "MediaIoBaseDownload", FakeDownload)

    excel_file = google_drive.download_excel_file_to_memory("sheet-file")

    assert excel_file.getvalue() == b"excel-bytes"
    assert files_resource.media_calls == []
    assert files_resource.export_calls == [
        {"fileId": "sheet-file", "mimeType": google_drive.EXCEL_MIME_TYPE}
    ]


def test_upload_or_replace_file_creates_when_missing(monkeypatch):
    files_resource = FakeFilesResource([{"files": []}], create_response={"id": "new-id"})
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )

    file_id = google_drive.upload_or_replace_file(
        filename="20260628.pptx",
        content=b"pptx",
        folder_id="output-folder",
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

    assert file_id == "new-id"
    assert files_resource.create_calls[0]["body"]["parents"] == ["output-folder"]
    assert files_resource.update_calls == []


def test_upload_or_replace_file_updates_existing(monkeypatch):
    files_resource = FakeFilesResource(
        [{"files": [{"id": "existing-id", "name": "20260628.pptx"}]}],
        update_response={"id": "existing-id"},
    )
    monkeypatch.setattr(
        google_drive,
        "build_drive_service",
        lambda: FakeDriveService(files_resource),
    )

    file_id = google_drive.upload_or_replace_file(
        filename="20260628.pptx",
        content=b"pptx",
        folder_id="output-folder",
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

    assert file_id == "existing-id"
    assert files_resource.update_calls[0]["fileId"] == "existing-id"
    assert files_resource.create_calls == []
