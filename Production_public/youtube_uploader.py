import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Define the OAuth 2.0 scopes required
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Function to get authenticated service from saved token
def get_authenticated_service(token_file, credentials_file):
    with open(token_file, 'r') as token:
        credentials = Credentials.from_authorized_user_info(json.load(token), SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            credentials = flow.run_local_server(port=0)

            # Save the new credentials
            with open(token_file, 'w') as token:
                token.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials)

# Define paths to credentials and token files
CREDENTIALS_FILES = {
    'left': 'Auth/left_upload.json',
    'right': 'Auth/right_upload.json',
    'centre': 'Auth/centre_upload.json',
    'ASMR': 'Auth/asmr_upload.json',
}

TOKEN_FILES = {
    'left': 'Auth/left_token.json',
    'right': 'Auth/right_token.json',
    'centre': 'Auth/centre_token.json',
    'ASMR': 'Auth/asmr_token.json',
}

# Function to upload video to YouTube
def upload_video_to_youtube(filepath, title, description, politic):
    if politic not in TOKEN_FILES or politic not in CREDENTIALS_FILES:
        print(politic)
        raise ValueError("Invalid politic value. Must be one of 'left', 'right', 'centre', 'asmr'.")

    token_file = TOKEN_FILES[politic]
    credentials_file = CREDENTIALS_FILES[politic]
    service = get_authenticated_service(token_file, credentials_file)

    # Upload video
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['tag1', 'tag2'],
            'categoryId': '25'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }

    media = MediaFileUpload(filepath, chunksize=-1, resumable=True)
    request = service.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = request.execute()
    print(f"Video uploaded successfully to {politic} channel: {response['id']}")

# # Test example
# if __name__ == "__main__":
#     video_filepath = 'final_videos/final_video_centre_0.mp4'
#     video_title = 'Test'
#     video_description = 'Test description'
#     video_politic = 'centre'  # Can be 'left', 'right', 'centre', 'asmr'

#     upload_video_to_youtube(video_filepath, video_title, video_description, video_politic)
