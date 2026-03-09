import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_account.json", scope
)

client = gspread.authorize(creds)


sheet_session = client.open("CAT_DB").worksheet("session")
sheet_response = client.open("CAT_DB").worksheet("response")


def save_session(pid, theta, se, item_count):

    sheet_session.append_row([pid, theta, se, item_count])


def save_response(pid, item_id, answer):

    sheet_response.append_row([pid, item_id, answer])
