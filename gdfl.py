from __future__ import print_function
import httplib2
import os
import sys
import codecs
import webbrowser

from operator import itemgetter, attrgetter
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse

    parent = argparse.ArgumentParser(parents=[tools.argparser])
    parent.add_argument("-f","--folder_id", help="Enter folder ID to list")
    flags = parent.parse_args()
except ImportError:
    flags = None


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Drive Folder List'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    client_secret = os.path.join(os.curdir, CLIENT_SECRET_FILE)
    if not client_secret:
        print('Follow the instructions in Step 1 on the following '
              'page:\nhttps://developers.google.com/drive/v3/web/quickstart/python')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'GADFL-secrets.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_folders(service, folder_id, level,Html_file):
    """Get's the folders in the parent folder
    """
    page_token = None
    while True:
      try:
        param = {}
        if page_token:
          param['pageToken'] = page_token

        results = service.files().list(
            q="'" + folder_id + "' in parents and mimeType='application/vnd.google-apps.folder'",
            fields="nextPageToken, files(id, name, parents, webViewLink, iconLink)",
            **param,).execute()

        items = results.get('files', [])
        items.sort(key=itemgetter('name'))
        level += 1
        if items:
            for item in items:
                current_id = item['id']
                indent = ' ' * level
                html_list2 = """
                <ul style="list-style: none;">
                <li><img src='"""+item['iconLink']+"""'><span><a href='"""+item['webViewLink']\
                             +"""' target='_blank'>"""+item['name']+"""</a></span>"""
                Html_file.write(html_list2)
                get_child_sub_folders(service, current_id, level,Html_file)
                Html_file.write("""
                  </li>
                </ul>""")
            page_token = results.get('nextPageToken')

        if not page_token:
          break

      except errors.HttpError as error:
        print('An error occurred: %s' % error)
        break

def get_child_sub_folders(service, parent_id, level,Html_file):
    """Get's the folders in the parent folder
    """
    page_token = None
    while True:
      try:
        param = {}
        if page_token:
          param['pageToken'] = page_token

        results = service.files().list(
            q="'" + parent_id + "' in parents and mimeType='application/vnd.google-apps.folder'",
            fields="nextPageToken, files(id, name, parents, webViewLink, iconLink)",
            **param).execute()

        items = results.get('files', [])
        items.sort(key=itemgetter('name'))
        prev_level = level
        level += 1
        if items:
            for item in items:
                child_id = item['id']
                indent = '  ' * level
                if level > prev_level:
                    html_list3 = """
                    <ul style="list-style: none;">
                    <li><img src='"""+item['iconLink']+"""'><span><a href='"""+item['webViewLink']\
                                 +"""' target='_blank'>"""+item['name']+"""</a></span>"""
                    Html_file.write(html_list3)
                else:
                    html_list3 = """
                    <li><img src='"""+item['iconLink']+"""'><span><a href='"""+item['webViewLink']\
                                 +"""' target='_blank'>"""+item['name']+"""</a></li>"""
                    Html_file.write(html_list3)

                prev_level = level
                get_child_sub_folders(service, child_id, level,Html_file)
            page_token = results.get('nextPageToken')
            Html_file.write("""
              </li>
            </ul>""")

        if not page_token:
          break

      except errors.HttpError as error:
        print('An error occurred: %s' % error)
        break


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    if not flags.folder_id:
        folder_id = 'root'
    else:
        folder_id = flags.folder_id

    level = 0

    html_file = 'GDFL-' + folder_id + '.html'
    Html_file = open(html_file, "w")
    html_start = """<!DOCTYPE html>
    <html>
      <head>
        <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
        <script type="text/javascript">
        $(function(){
        $('#example_tree').find('img').click(function(e){
            $(this).parent().children('UL').toggle();
        });
        });
        </script>
      </head>
      <body>"""
      #< body style = 'background-color:black;' > """
    Html_file.write(html_start)

    try:
        file = service.files().get(fileId=folder_id).execute()
        header = 'Folder structure for: ' + file['name']
        html_heading = """
        <div style='text-align:center;'>
        <h1>""" + header + """</h1>
        </div>"""
        Html_file.write(html_heading)
        html_list1 = """
        <UL id="example_tree" style="list-style: none;">
          <li><img src='https://ssl.gstatic.com/docs/doclist/images/icon_11_shared_collection_list_1.png'>
          <span>"""+file['name']+"""</span>"""
        Html_file.write(html_list1)
        print('Building folder structure for {0}'.format(file['name']))
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
    
    get_folders(service, folder_id, level,Html_file)

    html_end = """
          </li>
        </ul>
      </body>
    </html> """
    Html_file.write(html_end)
    Html_file.close()
    webbrowser.open(html_file)

if __name__ == '__main__':
    main()