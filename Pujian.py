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
SONGS_FOLDER = os.path.join(base_path, 'Songs' )
# SONGS_FOLDER = os.path.join(DOWNLOAD_FOLDER, "GRII" ,'GRII_Songs' )

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

        if not items:
            print('No folders found.')
        # else:
        #     print('Folders found in:', folder_id)
        #     for item in items:
        #         print(u'{0} ({1})'.format(item['name'], item['id']))
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
                print("downloaded folder: " + item['name'])
            else:
                download_file(item, destination_folder)
                print("downloaded file: " + item['name'])

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
    try: 
        folder_id = item['id']
        folder_name = item['name']

        #some weird folder structure, just use the first folder  
    except:
        folder_id = item[0]['id']
        folder_name = item[0]['name']
        
    song_number = str(song_number) # convert to string
    # change the folder name to the song number if it is not None
    temp_destination_folder = os.path.join(destination_folder, song_number) 
    folder_name = song_number
    # Create the destination folder if it does not exist
    if not os.path.exists(temp_destination_folder):
        os.makedirs(temp_destination_folder)
        os.chmod(temp_destination_folder, stat.S_IWGRP | stat.S_IWOTH | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IRUSR)

    return folder_id, folder_name
    



############### COMBINING ALL THE FUNCTIONS #####################
def download_new_song_pipeline(song_number): 
    # test_connection()
    get_list_folders(master_lagu_ibadah_folder_id)

    # open song folder with the name: number 
    folder_song_name = get_folder_id_by_name(song_number, master_lagu_ibadah_folder_id)
    folder_song_name_inside = get_list_folders(folder_song_name)
    print("folder song name inside: ", folder_song_name_inside)


    # if folder_song_name_inside is NoneType, then return
    if folder_song_name_inside is None:
        print("Folder not found")
        return

    # FOLDER SELECTION
    # if there are more than 1 folder in folder_song_name_inside, the download the one that have de or DE string in the name
    # otherwise download the first folder 
    if len(folder_song_name_inside) > 1:
        for folder in folder_song_name_inside:
            if "DE" in folder['name'] or "de" in folder['name'] or "De" in folder['name']:
                folder_song_name_inside = folder
                break
    else:
        folder_song_name_inside = folder_song_name_inside[0]

    #### check if the song is available locally if not, download from google drive
    song_folder_path = os.path.join(SONGS_FOLDER, str(song_number))
    if not os.path.exists(song_folder_path):
        # download the song folder from google drive
        download_folder(folder_song_name_inside, SONGS_FOLDER, song_number)

##################### download all songs ############################
def download_all_songs():
    # test_connection()
    print("parent folder:")
    get_list_folders(master_lagu_ibadah_folder_id)

    # open song folder with the name: number 
    master_lagu_ibadah = get_list_folders(master_lagu_ibadah_folder_id)
    print(master_lagu_ibadah)

    # structure : Master_Lagu_Ibadah > song number > song_number-DE again, but with DE > songs.jpg
    # we want to download all the songs in the folder 1-DE, 2DE, 3-DE, etc
    # so its a recursive function
    for song_number in master_lagu_ibadah:
        download_new_song_pipeline(song_number['name'])


download_all_songs()