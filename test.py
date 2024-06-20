import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive']

credentials_info = json.loads(os.getenv('GOOGLE_DRIVE_API_KEY'))
credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=credentials)

branch_name = os.getenv('GITHUB_REF').split('/')[-1]
folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

# Check if the folder with branch name exists
query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{branch_name}'"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
items = results.get('files', [])

if items:
  branch_folder_id = items[0]['id']
else:
  # Create a folder
  file_metadata = {
      'name': branch_name,
      'mimeType': 'application/vnd.google-apps.folder',
      'parents': [folder_id]
  }
  folder = drive_service.files().create(body=file_metadata, fields='id').execute()
  branch_folder_id = folder.get('id')

# Upload the file
file_metadata = {
  'name': 'resume.pdf',
  'parents': [branch_folder_id]
}
media = MediaFileUpload('resume.pdf', mimetype='application/pdf', resumable=True)

# Check if file exists
query = f"'{branch_folder_id}' in parents and name='resume.pdf'"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
items = results.get('files', [])

if items:
  # Update the existing file
  file_id = items[0]['id']
  updated_file = drive_service.files().update(
      fileId=file_id,
      media_body=media
  ).execute()
else:
  # Upload a new file
  file = drive_service.files().create(
      body=file_metadata,
      media_body=media,
      fields='id'
  ).execute()