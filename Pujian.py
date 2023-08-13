"""
This file get input 4 numbers such as : 112, 4, 700, 13
it searched first for a folder with the name of the number
if it doesnt found it, it will go to this google drive website: https://drive.google.com/drive/u/0/folders/1CjmdxteRGNpgSdYwMLf4UgH-uSWVXjnt
and download the folder with the name of the number
then it will unzip the folder and delete the zip file
then it will search for the file with the name of the number

if it found the file, it will open the file and search for a folder with the word "DE"
if it found the folder
    import all the JPG files in the folder and add to the pptx file

    if it doesnt found the folder
        it will search for the folder with the same numebr as its name
        if it found the folder
            import all the JPG files in the folder and add to the pptx file
        if it doesnt found the folder
            throw an error


"""


import json
import os
import io
import sys
from pptx import Presentation
from pptx.util import Inches
import stat

from pptx_creator import insert_slides_from_pict_folder


# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow # missing refresh_token
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
credentials_file = os.path.join(base_path, "mrii-automated-slides-service-accn-private-key.json")


# INPUT
HOME_DIR = os.path.expanduser("~")
DOWNLOAD_FOLDER = os.path.join(HOME_DIR, "Downloads")
SONG_NUMBER = "141" # TODO: get from input  
# Replace with the path to the destination folder on your local machine
# songs_folder = os.path.join(base_path, 'Songs' )
SONGS_FOLDER = os.path.join(DOWNLOAD_FOLDER, "GRII" ,'GRII_Songs' )

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

# ID of the folder you want to download from Google Drive
master_lagu_ibadah_folder_id = '1CjmdxteRGNpgSdYwMLf4UgH-uSWVXjnt'

# Read the credentials from the credentials.json file and parse it as a dictionary
with open(credentials_file, 'r') as f:
    credentials_data = json.load(f)

# Define the required scopes for the Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = None
service = None

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

def get_list_folders(folder_id):
    try:
        service = build('drive', 'v3', credentials=creds)

        query = "mimeType='application/vnd.google-apps.folder' and trashed = false and '{0}' in parents".format(folder_id)
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        while 'nextPageToken' in results:
            page_token = results['nextPageToken']
            results = service.files().list(q=query, fields="nextPageToken, files(id, name)", pageToken=page_token).execute()
            items.extend(results.get('files', []))

        if not items:
            print('No folders found.')

        return items

    except HttpError as error:
        print(f'An error occurred: {error}')

def get_folder_id_by_name(folder_name, parent_folder_id):
    try:
        service = build('drive', 'v3', credentials=creds)

        query = "name='{0}' and mimeType='application/vnd.google-apps.folder' and trashed = false and '{1}' in parents".format(folder_name, parent_folder_id)
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No folders found.')
            return None
        else:
            return items[0]['id']
    # file not found
    except IndexError:
        # throws error so user knows that the folder is not found and exit the program
        print("Folder not found")
        raise IndexError
    except HttpError as error:
        print(f'An error occurred: {error}')

    

def download_folder(google_folder_item, destination_folder, song_number):
    service = build('drive', 'v3', credentials=creds)

    g_folder_id, folder_name = make_local_folder_based_on_google_folder_name(google_folder_item, destination_folder, song_number)
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
            print(u'{0} ({1})'.format(item['name'], item['id']))
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                download_folder(item, destination_folder, song_number)
            else:
                download_file(item, destination_folder)

def download_file(item, destination_folder):
    service = build('drive', 'v3', credentials=creds)

    file_id = item['id']
    file_name = item['name']

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(destination_folder, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def make_local_folder_based_on_google_folder_name(item, destination_folder, song_number=None):
    folder_id = item['id']
    folder_name = item['name']
    song_number = str(song_number) # convert to string
    # change the folder name to the song number if it is not None
    temp_destination_folder = os.path.join(destination_folder, song_number) 
    folder_name = song_number
    # Create the destination folder if it does not exist
    if not os.path.exists(temp_destination_folder):
        os.makedirs(temp_destination_folder)
        os.chmod(temp_destination_folder, stat.S_IWGRP | stat.S_IWOTH | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IRUSR)

    return folder_id, folder_name

def folder_kenwyn_way(song_number, folder_song_name_list):
    """
    This function selects the appropriate folder from the list based on the given criteria.

    :param song_number: Not used in this function.
    :param folder_song_name_list: A list of folders with their names and IDs.
    :return: The selected folder or None if no suitable folder is found.

    folder_song_name_list = ["DE, "115"]
    folder_song_name_inside = "DE"
    folder_song_name_inside_3 = "115 DE"

    """

    # FOLDER SELECTION
    # Select the folder that contains "DE" or "de" or "De" in the name, otherwise, the first folder.

    for folder in folder_song_name_list:
        if folder['name'] == "DE":
            folder_song_name_inside = folder
            break
    else:
        # If no folder contains "DE" or "de" or "De", select the first folder in the list.
        if folder_song_name_list:
            folder_song_name_inside = folder_song_name_list[0]
        else:
            return None

    folder_song_name_inside_2_list = get_list_folders(folder_song_name_inside["id"])

    for folder in folder_song_name_inside_2_list:
        if "DE" in folder['name'].upper():
            folder_song_name_inside_3 = folder
            break
    else:
        folder_song_name_inside_3 = None

    return folder_song_name_inside_3



############### COMBINING ALL THE FUNCTIONS #####################
def download_new_song_pipeline(song_number): 
    # test_connection()
    print("Downloading song number: " + str(song_number))
    print("parent folder:")
    get_list_folders(master_lagu_ibadah_folder_id)

    # open song folder with the name: number 
    folder_song_name = get_folder_id_by_name(song_number, master_lagu_ibadah_folder_id)
    folder_song_name_inside = get_list_folders(folder_song_name)
    print(folder_song_name_inside)

    # if folder_song_name_insight is None, throw error
    if folder_song_name_inside is None:
        print ("Folder inside is not found, song_name:" + song_number)
        raise IndexError("Folder_song_name_inside is not found, it shouldnt be none")

    folder_song_name_inside = folder_kenwyn_way(song_number,folder_song_name_inside)
    if folder_song_name_inside is None:
        print("Folder not found according to kenwyn path")
        return

    #### check if the song is available locally if not, download from google drive
    song_folder_path = os.path.join(SONGS_FOLDER, str(song_number))
    if not os.path.exists(song_folder_path):
        # download the song folder from google drive
        download_folder(folder_song_name_inside, SONGS_FOLDER, song_number)
