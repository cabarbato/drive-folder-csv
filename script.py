import io
import os
import sys
import csv
import pickle
import requests
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

columns = ("id", "name", "url")

class FolderParser:
    def __init__(self):
        self.next_page = None
        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)

    def findFolder(self, folder_id):
        results = self.service.files().list( 
            supportsAllDrives="true",
            q=f"'{folder_id}' in parents",
            pageToken=self.next_page
            ).execute()
        files = results.get('files', [])

        if not files:
            print('No files located in that Drive URL')
        else:
            for file in files:
                self.writeRow(file)

            self.next_page = results.get('nextPageToken', None)
            if self.next_page: self.findFolder(folder_id)

    def writeRow(self, d):
        global download_images

        file_id = d.get("id")
        file_name = d.get("name").lower().replace(" ","-")
        file_url = os.getenv("OUTPUT_URL", default=None) + file_name
        drive_url = "https://drive.google.com/file/d/" + file_id

        self.downloadImage(file_id, file_name)

        csvwriter.writerow([
            file_id, 
            d.get("name"), 
            drive_url if not file_url else file_url
        ])
    
    def downloadImage(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO('./data/output/' + file_name, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))


if __name__ == "__main__":
    SCOPES = os.getenv("SCOPES", default=None).split(',')

    if len(sys.argv) > 1:
        if len(sys.argv) is 1:
            filename, URL = sys.argv
            download_images = 0
        else: filename, URL, download_images = sys.argv
    else: 
        URL = os.getenv("DEFAULT_URL", default=None)
        download_images = 0

    while True:
        if not URL: 
            URL = input("Enter the URL to the Drive folder: ")
        try:
            requests.get(URL)
            break
        except requests.ConnectionError as exception:
            print(URL + " is not a valid URL")
            URL = None 
    
    folder_id = URL.split("/")[-1]

    with open(f'./data/output/drive_contents_{folder_id}.csv', 'w', newline='') as output_file:
        csvwriter = csv.writer(output_file)    
        csvwriter.writerow(columns)   
        FolderParser().findFolder(folder_id)