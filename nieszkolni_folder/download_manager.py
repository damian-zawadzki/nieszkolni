from __future__ import print_function

import os.path

import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json


class DownloadManager:

    DOCUMENT_ID = '1zT9E3gUXIXfg4kFUf0wwk2plmDDY8UZ9qgoZkXAv8PY'

    def __init__(self):
        pass

    def main(self):
        SCOPES = ['https://www.googleapis.com/auth/documents']

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

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

        service = build('docs', 'v1', credentials=creds)
        return service

    def create_document(self):
        service = self.main()

        title = "Joe Doe's Notebook"

        body = {
            'title': title
        }

        doc = service.documents().create(body=body).execute()

        print('Created document with title: {0}'.format(
            doc.get('title')))
