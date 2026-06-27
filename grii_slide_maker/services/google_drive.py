"""Google Drive API helpers for loading slide images."""

import io
import os
import re
from typing import Any

import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from grii_slide_maker.models import DriveFolder, DriveImageFile, DriveItem, SongImageSet

SCOPES = ["https://www.googleapis.com/auth/drive"]
GOOGLE_SHEETS_MIME_TYPE = "application/vnd.google-apps.spreadsheet"
EXCEL_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
creds = None


def test_connection() -> None:
    """Print the names and ids of the first 10 Drive files."""
    global creds

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try_build_drive_service(creds)


def try_build_drive_service(active_creds: Any) -> None:
    try:
        drive_service = build("drive", "v3", credentials=active_creds)

        results = (
            drive_service.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return

        print("Files:")
        for item in items:
            print("{0} ({1})".format(item["name"], item["id"]))
    except HttpError as error:
        print(f"An error occurred: {error}")


def connect_service_account_streamlit() -> None:
    """Connect to Drive with Streamlit service account secrets."""
    global creds

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES,
            )


def ensure_drive_connected() -> None:
    if not creds or not creds.valid:
        connect_service_account_streamlit()


def build_drive_service() -> Any:
    ensure_drive_connected()
    return build("drive", "v3", credentials=creds)


def get_list_folders(folder_id: str) -> list[DriveFolder] | None:
    try:
        drive_service = build_drive_service()

        query = (
            "mimeType='application/vnd.google-apps.folder' "
            f"and trashed = false and '{folder_id}' in parents"
        )
        results = (
            drive_service.files()
            .list(q=query, fields="nextPageToken, files(id, name, mimeType)")
            .execute()
        )
        items = results.get("files", [])

        while "nextPageToken" in results:
            page_token = results["nextPageToken"]
            results = (
                drive_service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageToken=page_token,
                )
                .execute()
            )
            items.extend(results.get("files", []))

        if not items:
            print("No folders found.")

        return [DriveFolder.model_validate(item) for item in items]

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_folder_id_by_name(folder_name: str, parent_folder_id: str) -> str | None:
    try:
        drive_service = build_drive_service()

        query = (
            f"name='{folder_name}' "
            "and mimeType='application/vnd.google-apps.folder' "
            f"and trashed = false and '{parent_folder_id}' in parents"
        )
        results = (
            drive_service.files()
            .list(q=query, fields="nextPageToken, files(id, name, mimeType)")
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No folders found.")
            return None

        return DriveFolder.model_validate(items[0]).id
    except IndexError:
        print("Folder not found")
        raise
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def download_file(item: dict[str, Any], destination_folder: str) -> None:
    drive_item = DriveItem.model_validate(item)
    drive_service = build_drive_service()

    request = drive_service.files().get_media(fileId=drive_item.id)
    with io.FileIO(os.path.join(destination_folder, drive_item.name), "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

    print("Downloaded file: " + drive_item.name)


def download_excel_file_to_memory(file_id: str) -> io.BytesIO:
    """Download an Excel workbook, exporting Google Sheets to xlsx when needed."""
    drive_service = build_drive_service()
    metadata = (
        drive_service.files()
        .get(fileId=file_id, fields="id, name, mimeType")
        .execute()
    )

    if metadata.get("mimeType") == GOOGLE_SHEETS_MIME_TYPE:
        request = drive_service.files().export_media(
            fileId=file_id,
            mimeType=EXCEL_MIME_TYPE,
        )
    else:
        request = drive_service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()

    fh.seek(0)
    return fh


def upload_or_replace_file(
    *,
    filename: str,
    content: bytes,
    folder_id: str,
    mime_type: str,
) -> str:
    """Upload a file to Drive, replacing the first file with the same name."""
    drive_service = build_drive_service()
    query = (
        f"name='{filename}' "
        f"and trashed = false and '{folder_id}' in parents"
    )
    results = (
        drive_service.files()
        .list(q=query, fields="files(id, name, mimeType)")
        .execute()
    )
    existing_files = results.get("files", [])
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=True)

    if existing_files:
        file_id = existing_files[0]["id"]
        result = (
            drive_service.files()
            .update(
                fileId=file_id,
                media_body=media,
                fields="id",
            )
            .execute()
        )
        return result["id"]

    body = {
        "name": filename,
        "parents": [folder_id],
        "mimeType": mime_type,
    }
    result = (
        drive_service.files()
        .create(
            body=body,
            media_body=media,
            fields="id",
        )
        .execute()
    )
    return result["id"]


def save_images_from_google_folder_to_memory(folder_id: str) -> dict[str, Any]:
    drive_service = build_drive_service()

    response = (
        drive_service.files()
        .list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)")
        .execute()
    )
    files = response.get("files", [])
    images = {}

    for file in files:
        drive_item = DriveItem.model_validate(file)
        if not drive_item.is_image:
            continue

        image_file = DriveImageFile.model_validate(file)
        request = drive_service.files().get_media(fileId=image_file.id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        images[image_file.name] = fh
        print("Downloaded file: " + image_file.name)

    sorted_images = dict(
        sorted(
            images.items(),
            key=lambda item: int(re.findall(r"\d+", item[0])[0])
            if re.findall(r"\d+", item[0])
            else 0,
        )
    )

    return SongImageSet.model_validate({"images": sorted_images}).images
