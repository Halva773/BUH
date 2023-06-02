from __future__ import print_function


import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
what_has_been_sent_id = []
subject = ""
from_name = ""
decoded_data = ''

auth = " login : apigml01@gmail.com, pass : pass@@@@"


def check_email(users_ids):
    import botstart
    global what_has_been_sent_id, decoded_data, subject, from_name
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds/creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        print("unread - ", len(messages))
        if len(messages) == 0:
            what_has_been_sent_id = []

        ################################################################################################
        message_count = 0

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            # print(msg)
            message_count = message_count + 1
            email_data = msg['payload']['headers']
            # print(type(email_data))

            for values in email_data:
                name = values["name"]
                if name == "From":
                    from_name = values["value"]
                    # print(from_name)
                    subject = " ".join([j['value'] for j in email_data if j["name"] == "Subject"])

                    # print("Subject: ", subject)
                    # bot.send_message(chat_id=489311844, text=f" Subject: {subject}")
                    # print("From: ", from_name)

            for p in msg["payload"]["parts"]:

                # "text/plain",
                if p["mimeType"] in ["text/html", 'text/plain']:

                    decoded_data = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
                    # bot.send_message(chat_id=489311844, text=f" Message: {decoded_data}")
                    if message["id"] in what_has_been_sent_id:
                        pass
                    else:
                        what_has_been_sent_id.append(message["id"])
                        # print(f"🔴Subject: {subject} \n🟡From: {from_name} \n🟢Message: {decoded_data}")
                        botstart.send_message(-1001912865564, f"🔴Subject: {subject} \n🟡From: {from_name} \n🟢Message: {decoded_data}")
                else:
                    try:
                        par = (p["parts"])
                        # print(par)
                        for i in par:
                            try:
                                decoded_data = base64.urlsafe_b64decode(i["body"]["data"]).decode("utf-8")
                                # bot.send_message(chat_id=489311844, text=f" Message: {decoded_data}")
                                if message["id"] in what_has_been_sent_id:
                                    pass
                                else:
                                    what_has_been_sent_id.append(message["id"])
                                    # print(f"🔴Subject: {subject} \n🟡From: {from_name} \n🟢Message: {decoded_data}")

                                    botstart.send_message(-1001912865564, f"🔴Subject  : {subject} \n\n🟡From : {from_name} \n\n🟢Message : {decoded_data}")
                            except:
                                pass
                    except KeyError:
                        pass

    except HttpError as error:
        print(f'An error occurred: {error}')
