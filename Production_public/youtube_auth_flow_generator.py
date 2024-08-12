import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the OAuth 2.0 scopes required
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Function to get authenticated service and save the credentials
def get_authenticated_service(credentials_file, token_file):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    credentials = flow.run_local_server(port=0)

    # Save the credentials for later use
    with open(token_file, 'w') as token:
        token.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials)

# List of channels and corresponding credentials files
channels = {
    'left': 'Auth/left_upload.json',
    'right': 'Auth/right_upload.json',
    'centre': 'Auth/centre_upload.json',
    'asmr': 'Auth/asmr_upload.json',
}

# Authorize each channel and save the tokens
for channel, credentials_file in channels.items():
    token_file = f'{channel}_token.json'
    print(f'Authorizing {channel} channel...')
    service = get_authenticated_service(credentials_file, token_file)
    print(f'{channel} channel authorized and token saved to {token_file}.')
