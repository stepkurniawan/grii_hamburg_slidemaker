"""Download song slide images from Google Drive and load them into memory."""


import os
import io
import re
import sys
from typing import Any
import stat
import streamlit as st

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow # missing refresh_token
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from grii_slide_maker.config import Settings
from grii_slide_maker.models import DriveFolder, DriveImageFile, DriveItem, SongImageSet

base_path = getattr(
    sys,
    "_MEIPASS",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)


# INPUT
HOME_DIR = os.path.expanduser("~")
DOWNLOAD_FOLDER = os.path.join(HOME_DIR, "Downloads")
SONGS_FOLDER = os.path.join(base_path, 'songs' )

settings = Settings()


# Define the required scopes for the Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
global creds, service
creds = None
service = None

############################## FUNCTIONS ##############################

def st_print(text):
    st.write(text)
    print(text)



def test_connection():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try_build_drive_service(creds)

def try_build_drive_service(creds):
    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

def connect_service_account_streamlit():
    # service account doenst need to store user credentials
    
    global creds

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES,
            )
    try_build_drive_service(creds)


def ensure_drive_connected():
    if not creds or not creds.valid:
        connect_service_account_streamlit()


def get_list_folders(folder_id, creds):
    try:
        ensure_drive_connected()
        active_creds = globals()["creds"]
        service = build('drive', 'v3', credentials=active_creds)

        query = "mimeType='application/vnd.google-apps.folder' and trashed = false and '{0}' in parents".format(folder_id)
        results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        while 'nextPageToken' in results:
            page_token = results['nextPageToken']
            results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)", pageToken=page_token).execute()
            items.extend(results.get('files', []))

        if not items:
            print('No folders found.')

        return [DriveFolder.model_validate(item) for item in items]

    except HttpError as error:
        print(f'An error occurred: {error}')

def get_folder_id_by_name(folder_name, parent_folder_id):
    try:
        ensure_drive_connected()
        service = build('drive', 'v3', credentials=creds)

        query = "name='{0}' and mimeType='application/vnd.google-apps.folder' and trashed = false and '{1}' in parents".format(folder_name, parent_folder_id)
        results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            print('No folders found.')
            return None
        else:
            return DriveFolder.model_validate(items[0]).id
    # file not found
    except IndexError:
        # throws error so user knows that the folder is not found and exit the program
        print("Folder not found")
        raise IndexError
    except HttpError as error:
        print(f'An error occurred: {error}')

    

def download_folder(google_folder_item, destination_folder, song_number):
    google_folder = DriveFolder.model_validate(google_folder_item)
    st_print("Downloading folder: " + google_folder.name)
    ensure_drive_connected()
    service = build('drive', 'v3', credentials=creds)

    g_folder_id, folder_name = make_local_folder_based_on_google_folder_name(google_folder, destination_folder, song_number)
    destination_folder = os.path.join(destination_folder, folder_name)
    print("destination_folder for songs: " + destination_folder)

    query = "'{0}' in parents".format(g_folder_id)
    results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            drive_item = DriveItem.model_validate(item)
            print(u'{0} ({1})'.format(drive_item.name, drive_item.id))
            if drive_item.is_folder:
                download_folder(drive_item, destination_folder, song_number)
            else:
                download_file(drive_item, destination_folder)

def download_file(item, destination_folder):
    drive_item = DriveItem.model_validate(item)
    ensure_drive_connected()
    service = build('drive', 'v3', credentials=creds)

    file_id = drive_item.id
    file_name = drive_item.name

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(destination_folder, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    st_print("Downloaded file: " + file_name)

def make_local_folder_based_on_google_folder_name(item, destination_folder, song_number=None):
    folder = DriveFolder.model_validate(item)
    folder_id = folder.id
    folder_name = folder.name
    song_number = str(song_number) # convert to string
    # change the folder name to the song number if it is not None
    temp_destination_folder = os.path.join(destination_folder, song_number) 
    folder_name = song_number
    # Create the destination folder if it does not exist
    if not os.path.exists(temp_destination_folder):
        os.makedirs(temp_destination_folder)
        os.chmod(temp_destination_folder, stat.S_IWGRP | stat.S_IWOTH | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IRUSR)

    return folder_id, folder_name

##### adding fall back plan to take english songs if german songs are not found

def folder_english_way(song_number, folder_song_name_list):
    """
    This function selects the appropriate folder from the list based on the given criteria.

    :param song_number: Not used in this function.
    :param folder_song_name_list: A list of folders with their names and IDs.
    :return: The selected folder or None if no suitable folder is found.

    example: Master Lagu Ibadah > 262 > 262 > Slide1.JPG...SlideN.JPG

    folder_song_name_list = ["262"]
    folder_song_name_inside = ["262"]
    """
    for folder in folder_song_name_list:
        drive_folder = DriveFolder.model_validate(folder)
        if drive_folder.name == song_number:
            folder_song_name_inside = folder
            break
    else:
        # If no folder contains "DE" or "de" or "De", select the first folder in the list.
        if folder_song_name_list:
            folder_song_name_inside = folder_song_name_list[0]
        else:
            return None

    return folder_song_name_inside




################## IN MEMORY IMAGE SAVING ##################
def save_images_from_google_folder_to_memory(folder_id) -> dict[str, Any]:
    # folder_id is the ID of the Google Drive folder containing the images
    ensure_drive_connected()
    drive_service = build('drive', 'v3', credentials=creds)

    # Retrieve a list of files in the folder
    response = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
    files = response.get('files', [])

    # Create a dictionary to store the image data
    song_images_dict = {}

    # Loop through files and add image data to the dictionary
    for file in files:
        drive_item = DriveItem.model_validate(file)
        if drive_item.is_image:
            image_file = DriveImageFile.model_validate(file)
            # Get the file ID
            file_id = image_file.id

            # Get the file name
            file_name = image_file.name

            # Create a list entry for the file name
            song_images_dict[file_name] = {}

            # Get the file data
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            # Add the file data to the dictionary entry
            song_images_dict[file_name] = fh

            print("Downloaded file: " + file_name)

    # sort the dictionary by the key
    song_images_dict = dict(sorted(song_images_dict.items(), key=lambda x: int(re.findall(r'\d+', x[0])[0]) if re.findall(r'\d+', x[0]) else 0))

    return SongImageSet.model_validate({"images": song_images_dict}).images



############### COMBINING ALL THE FUNCTIONS #####################
def download_new_song_pipeline(song_number): 
    st_print("Downloading song number: " + str(song_number))
    master_lagu_ibadah_folder_id = settings.GOOGLE_DRIVE_SONG_MASTER_FOLDER_ID

    get_list_folders(master_lagu_ibadah_folder_id, creds)

    # open song folder with the name: number 
    folder_song_name = get_folder_id_by_name(song_number, master_lagu_ibadah_folder_id)
    folder_song_name_inside = get_list_folders(folder_song_name, creds)
    print(folder_song_name_inside)

    # if folder_song_name_insight is None, throw error
    if folder_song_name_inside is None:
        st_print ("Folder inside is not found, song_name:" + song_number)
        st.error("Folder_song_name_inside is not found, I cannot find the song number in the Master Folder: " + str(song_number))
        raise IndexError("Folder_song_name_inside is not found, I cannot find the song number in the Master Folder: " + str(song_number))

    folder_song_name_inside2 = folder_english_way(song_number, folder_song_name_inside)
    if folder_song_name_inside2 is None:
        st.error("English folder not found, please check google drive path to make sure this is intended, song: " + str(song_number))
        return None

    #### download from google drive
    st_print("Downloading from google drive song number: " + str(song_number))
    song_folder = DriveFolder.model_validate(folder_song_name_inside2)
    song_images = save_images_from_google_folder_to_memory(song_folder.id)
    return song_images

    
##### TEST #####
# download_new_song_pipeline(5)

