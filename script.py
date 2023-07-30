import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from h11 import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_KEY = 'YOUR API KEY'
CLIENT_SECRETS_FILE = 'client_secrets.json'
CREDENTIALS_FILE = 'credentials.json'
FOLDER_PATH = '../myVideos'
DESCRIPTION_TEMPLATE = 'This is the description template.'
CATEGORY_ID = 1

def get_authenticated_service():
    credentials = None

    if os.path.exists(CREDENTIALS_FILE):
        credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)

        with open(CREDENTIALS_FILE, 'w') as credentials_file:
            credentials_file.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials, developerKey=API_KEY)

def upload_video(youtube, video_path, title, description, privacy_status, category_id):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    media_file = MediaFileUpload(video_path)

    try:
        response = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media_file
        ).execute()

        print('Video uploaded successfully.')
        return response['id']
    except Exception as e:
        print('An error occurred:', str(e))
        return None

if __name__ == '__main__':
    youtube = get_authenticated_service()

    for file_name in os.listdir(FOLDER_PATH):
        video_path = os.path.join(FOLDER_PATH, file_name)
        title = os.path.splitext(file_name)[0]
        description = DESCRIPTION_TEMPLATE.replace('<title>', title)

        upload_video(youtube, video_path, title, description, 'private', CATEGORY_ID)
