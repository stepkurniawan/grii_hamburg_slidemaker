# google connections

import streamlit as st
import os
import sys

import google_auth as ga_module


# pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()

################################## GLOBALS ##################################

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
credentials_file = os.path.join(base_path, "mrii-automated-slides-service-accn-private-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


################################## FUNCTIONS ##################################

def test_connection(creds):
    ga_module.test_connection(creds)

def try_build_drive_service(creds):
    ga_module.try_build_drive_service(creds)

def test_connection_using_TOML_file(creds):
    ga_module.test_connection_using_TOML_file(creds)

def test_connection_using_streamlit_secrets(creds):
    ga_module.test_connection_using_streamlit_secrets(creds)

def connect_service_account_streamlit(creds):
    ga_module.connect_service_account_streamlit(creds)

