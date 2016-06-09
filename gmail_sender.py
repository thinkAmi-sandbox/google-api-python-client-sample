import httplib2
import os

import apiclient
import oauth2client
import argparse
flags = argparse.ArgumentParser(
    parents=[oauth2client.tools.argparser]
).parse_args()

import base64
from email.mime.text import MIMEText
from email.utils import formatdate
import traceback

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = "https://www.googleapis.com/auth/gmail.send"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "MyGmailSender"

MAIL_FROM = "example@gmail.com"
MAIL_TO = "example+alias@gmail.com"

def get_credentials():
    script_dir =os.path.abspath(os.path.dirname(__file__)) 
    credential_dir = os.path.join(script_dir, ".credentials")

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   "my-gmail-sender.json")

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = oauth2client.tools.run_flow(flow, store, flags)
        print("Storing credentials to " + credential_path)
    return credentials


def create_message():
    message = MIMEText("Gmail body: Hello world!")
    message["from"] = MAIL_FROM
    message["to"] = MAIL_TO
    message["subject"] = "gmail api test"
    message["Date"] = formatdate(localtime=True)

    byte_msg = message.as_string().encode(encoding="UTF-8")
    byte_msg_b64encoded = base64.urlsafe_b64encode(byte_msg)
    str_msg_b64encoded = byte_msg_b64encoded.decode(encoding="UTF-8")

    return {"raw": str_msg_b64encoded}


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build("gmail", "v1", http=http)

    try:
        result = service.users().messages().send(
            userId=MAIL_FROM,
            body=create_message()
        ).execute()

        print("Message Id: {}".format(result["id"]))

    except apiclient.errors.HttpError:
        print("------start trace------")
        traceback.print_exc()
        print("------end trace------")


if __name__ == "__main__":
    main()