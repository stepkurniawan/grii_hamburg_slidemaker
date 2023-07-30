# google connections

import toml

import os
import sys

# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow # missing refresh_token
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


################################## GLOBALS ##################################

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
# credentials_file = os.path.join(base_path, "mrii-automated-slides-service-accn-private-key.json")

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


################################## FUNCTIONS ##################################

def test_connection(creds):
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

def test_connection_using_TOML_file(creds):
    """
    # pip install toml
    toml file: 
    client_id = "974376972016-v9nehu4s0me054gh9n631m4n4qssj4oi.apps.googleusercontent.com"
    client_secret = "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"

    Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    """

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
                
                with open('credentials.toml') as f:
                    data = toml.load(f)
                    client_id = data['client_id']
                    client_secret = data['client_secret']
    
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.toml', SCOPES)
                creds = flow.run_local_server(port=0)


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

    
