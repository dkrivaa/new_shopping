import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import json
from dotenv import load_dotenv
import streamlit as st


def download_from_drive(file_name):
    """ This function downloads the db from google drive """
    load_dotenv()
    folder_id = os.getenv("FOLDER_ID")
    # Load credentials from Streamlit secrets
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT")),
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    # Build the Drive API service
    service = build("drive", "v3", credentials=credentials)

    # Search for the file in the specified folder
    results = service.files().list(
        q=f"'{folder_id}' in parents and name='{file_name}'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if not files:
        st.error(f"No file named {file_name} found in folder!")
    else:
        file_id = files[0]["id"]
        # st.info(f"Downloading {file_name} from Drive...")

        # Download the file
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # st.write(f"Download {int(status.progress() * 100)}%.")

        # st.success(f"✅ Downloaded {file_name} to local directory.")


def upload_to_drive(db_name):
    """ This file uploads the db to google drive """
    load_dotenv()
    folder_id = os.getenv("FOLDER_ID")
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT")),
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=credentials)

    # Find existing file by name in the folder
    query = f"name = '{db_name}' and '{folder_id}' in parents and trashed = false"
    response = service.files().list(q=query, fields="files(id)").execute()
    files = response.get("files", [])

    if not files:
        print(f"❌ File '{db_name}' not found in folder. No update performed.")
        return

    file_id = files[0]['id']  # use the first match
    media = MediaFileUpload(db_name, mimetype="application/x-sqlite3")

    # Perform the update using fileId
    service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()

