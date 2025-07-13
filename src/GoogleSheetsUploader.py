import os

import httplib2
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load variables from .env into the environment
load_dotenv()

CREDENTIALS_FILE = os.getenv('OAUTH_CRED_FILE_NAME')
SPREADSHEET_ID = os.getenv('GOOGLE_SPREAD_SHEET_ID')
WORKSHEET_NAME = os.getenv('WORK_SHEET_NAME')

class GoogleSheetsUploader:
    def __init__(self):
        # Define the scope of the application.
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        try:
            service = build("sheets", "v4", credentials=creds)
            self.sheet = service.spreadsheets()
        except HttpError as err:
            raise err

    def append_row(self, row_values: list):
        body = {
            'values': [row_values]
        }

        try:
            result = self.sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=(WORKSHEET_NAME + "!A1"),
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            updated_cells = result.get("updates", {}).get("updatedCells", 0)
            print(f"Successfully appended row: {updated_cells} cells updated.")
        except Exception as e:
            print("Error uploading row:", e)

    def destroy_token_file(self):
        token_file = "token.json"
        if os.path.exists(token_file):
            try:
                os.remove(token_file)
                print("Token file deleted successfully.")
            except Exception as e:
                print("Failed to delete token file:", e)
        else:
            print("No token file found to delete.")


# Example usage:
if __name__ == '__main__':
    # Sample data to upload – these are the provided values.
    row_data = [
        202.14,
        3036567306000.0,
        32.09,
        125675000000.0,
        96150000000.0,
        1.440276820755565,
        0.27943676707790227,
        395760000000.0,
        46.51884980796442,
        1,
        2,
        3,
        4.609024563666496,
        False,
        5.154213727193745,
        5.913634141819346,
        3,
        False
    ]

    try:
        uploader = GoogleSheetsUploader()
        uploader.append_row(row_data)
    except Exception as e:
        print("Error uploading row:", e)
