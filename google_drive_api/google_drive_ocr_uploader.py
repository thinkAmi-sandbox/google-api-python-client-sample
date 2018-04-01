import argparse
import os
import pathlib

import httplib2
from apiclient import discovery
from googleapiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


UPLOAD_FILE_NAME = '2017h29a_fe_am_qs.pdf'

# pdfをGoogle DocsにすることでOCRしてくれる
# MIME typeは以下にある
# https://developers.google.com/drive/v3/web/mime-types
MIME_TYPE = 'application/vnd.google-apps.document'

# get_credentials()関数まわりは公式ドキュメントよりコピペ(Python2.6部分は削除)
# https://developers.google.com/drive/v3/web/quickstart/python#step_3_set_up_the_sample

# scopeは以下より
# https://developers.google.com/drive/v3/web/about-auth
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'ipa-google-drive-api-client'

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def upload_with_ocr():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    local_file_path = pathlib.Path(__file__).resolve().parent.joinpath(UPLOAD_FILE_NAME)

    media_body = MediaFileUpload(local_file_path, mimetype=MIME_TYPE, resumable=True)

    body = {
        # 拡張子付、パスなしのファイル名を与える
        # 拡張子なし(file_path.stem)だと、HTTP400エラーになる
        'name': local_file_path.name,
        'mimeType': MIME_TYPE,
    }

    service.files().create(
        body=body,
        media_body=media_body,
        # OCRの言語コードは、ISO 639-1 codeで指定
        # https://developers.google.com/drive/v3/web/manage-uploads
        ocrLanguage='ja',
    ).execute()


if __name__ == '__main__':
    upload_with_ocr()
