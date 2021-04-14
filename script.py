import os
import sys
import csv
import pickle
import requests
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

    def findFolder(self, folder_id):
        service = build('drive', 'v3', credentials=self.creds)
        results = service.files().list( 
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
        file_id = d.get("id")
        file_name = d.get("name")
        csvwriter.writerow([file_id, file_name, "https://drive.google.com/file/d/" + file_id])


if __name__ == "__main__":
    SCOPES = os.getenv("SCOPES", default=None).split(',')

    if len(sys.argv) > 1:
        filename, URL = sys.argv
    else: 
        URL = os.getenv("DEFAULT_URL", default=None)

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