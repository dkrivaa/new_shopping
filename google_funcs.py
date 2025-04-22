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
        json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"),
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
        st.info(f"Downloading {file_name} from Drive...")

        # Download the file
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            st.write(f"Download {int(status.progress() * 100)}%.")

        st.success(f"✅ Downloaded {file_name} to local directory.")


def upload_to_drive(db_name):
    """ This file uploads the db to google drive """
    load_dotenv()
    folder_id = os.getenv("FOLDER_ID")
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"]),
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=credentials)

    file_metadata = {"name": db_name, "parents": [folder_id]}
    media = MediaFileUpload(db_name, mimetype="application/x-sqlite3")

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    st.success(f"Uploaded to Drive with ID: {uploaded['id']}")