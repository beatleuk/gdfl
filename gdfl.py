from __future__ import print_function
import httplib2
import os
import sys
import codecs
import webbrowser

from operator import itemgetter, attrgetter
from apiclient import errors, discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse

    parent = argparse.ArgumentParser(parents=[tools.argparser])
    parent.add_argument("-f", "--folder_id", help="Enter folder ID to list")
    parent.add_argument("-c", "--files", action='store_false',
                        help="To include child files in folders")
    flags = parent.parse_args()
except ImportError:
    flags = None

# This script is dervived from Googles own Google Drive API Python
# Quickstart and pulls together many of the reference samples.

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/dgdfl-secrets.json
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
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
                                   'gdfl-secrets.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_folders(service, folder_id, level, Html_file, folders_only, drivetype):
    """Get's the folders in the parent folder
    """
    global FOLDERCOUNT
    global FILECOUNT
    global DEEPEST
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token

            if folders_only == True:
                query = "'" + folder_id + "' in parents and mimeType='application/vnd.google-apps.folder'"
            else:
                query = "'" + folder_id + "' in parents"

            if drivetype == 'Shared Drive':
                results = service.files().list(
                    q=query,
                    driveId=folder_id,
                    corpora='drive',
                    includeItemsFromAllDrives='true',
                    supportsAllDrives='true',
                    fields="nextPageToken, files(id, name, parents, webViewLink, iconLink, mimeType)").execute()
            else:
                results = service.files().list(
                    q=query, orderBy='folder',
                    fields="nextPageToken, files(id, name, parents, webViewLink, iconLink)",
                    **param).execute()
            
            items = results.get('files', [])
            items.sort(key=itemgetter('name'))
            level += 1
            if items:
                for item in items:
                    if drivetype == 'Shared Drive':
                        if item['mimeType'] == 'application/vnd.google-apps.folder':
                            FOLDERCOUNT += 1
                            if level > DEEPEST:
                                DEEPEST = level
                        else:
                            FILECOUNT += 1
                    current_id = item['id']
                    itemname = item['name']
                    #if isinstance(itemname, str):
                        #childname = unicode(childname, "utf-8")
                    indent = ' ' * level
                    depth = str(level)
                    html_list2 = """
                <ul style="list-style: none;">
                <li><img src='""" + item['iconLink'] + """'><span><a href='""" + item['webViewLink'] \
                                 + """' target='_blank'> """ + itemname + """</a></span>"""
                    if (sys.version_info < (3, 0)):
                        Html_file.write(html_list2.encode("utf-8"))
                    else:
                        Html_file.write(html_list2)
                    get_child_sub_folders(service, current_id, level, Html_file, folders_only, folder_id, drivetype)
                    Html_file.write("""
                  </li>
                </ul>""")
                page_token = results.get('nextPageToken')

            if not page_token:
                break

        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            break

def get_child_sub_folders(service, parent_id, level, Html_file, folders_only, folder_id, drivetype):
    """Get's the folders in the child folder
    """
    global FOLDERCOUNT
    global FILECOUNT
    global DEEPEST
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token

            if folders_only == True:
                query = "'" + parent_id + "' in parents and mimeType='application/vnd.google-apps.folder'"
            else:
                query = "'" + parent_id + "' in parents"

            if drivetype == 'Shared Drive':
                results = service.files().list(
                    q=query,
                    driveId=folder_id,
                    corpora='drive',
                    includeItemsFromAllDrives='true',
                    supportsAllDrives='true',
                    fields="nextPageToken, files(id, name, parents, webViewLink, iconLink, mimeType)").execute()
            else:
                results = service.files().list(
                    q=query, orderBy='folder',
                    fields="nextPageToken, files(id, name, parents, webViewLink, iconLink)",
                    **param).execute()

            items = results.get('files', [])
            items.sort(key=itemgetter('name'))
            prev_level = level
            level += 1
            if items:
                for item in items:
                    if drivetype == 'Shared Drive':
                        if item['mimeType'] == 'application/vnd.google-apps.folder':
                            FOLDERCOUNT += 1
                            if level > DEEPEST:
                                DEEPEST = level
                        else:
                            FILECOUNT += 1
                    child_id = item['id']
                    childname = item['name']
                    #if isinstance(childname, str):
                        #childname = unicode(childname, "utf-8")
                    #print(item['webViewLink'])
                    indent = '  ' * level
                    depth = str(level)
                    if level > prev_level:
                        html_list3 = """
                    <ul style="list-style: none;">
                    <li><img src='""" + item['iconLink'] + """'><span><a href='""" + item['webViewLink'] \
                                     + """' target='_blank'> """ + childname + """</a></span>"""
                        if (sys.version_info < (3, 0)):
                            Html_file.write(html_list3.encode("utf-8"))
                        else:
                            Html_file.write(html_list3)
                    else:
                        html_list3 = """
                    <li><img src='""" + item['iconLink'] + """'><span><a href='""" + item['webViewLink'] \
                                     + """' target='_blank'> """ + childname + """</a></li>"""
                        if (sys.version_info < (3, 0)):
                            Html_file.write(html_list3.encode("utf-8"))
                        else:
                            Html_file.write(html_list3)

                    prev_level = level
                    get_child_sub_folders(service, child_id, level, Html_file, folders_only, folder_id, drivetype)
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
    """Uses Google Drive API to get the parent folder
    Gets the parent folder specified in args or uses the users Root folder
    Calls the function to get sub folders and loops through all child folders.
    Produces the html file output and opens it in the default browser.
    """
    foldername = ''
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    if not flags.folder_id:
        folder_id = 'root'
        drivetype = 'My Drive'
    else:
        folder_id = flags.folder_id

        try:
            folder = service.files().get(fileId=folder_id).execute()
            foldername = folder['name']
            drivetype = 'My Drive'
            print("Folder ID " + folder_id + " is a Google Drive Folder called: " + foldername)
        except errors.HttpError as error:
            try:
                folder = service.drives().get(
                  driveId=folder_id,
                  useDomainAdminAccess='true').execute()
                foldername = folder['name']
                drivetype = 'Shared Drive'
                print("Folder ID " + folder_id + " is a Shared Drive named: " + foldername)
            except errors.HttpError as error:
                foldername = ''

    if not foldername:
       print('An error occurred %s' % error)
       exit()

    
    if (sys.version_info < (3, 0)):
        if isinstance(foldername, str):
            foldername = unicode(foldername, "utf-8")

    folders_only = flags.files
    level = 0

    html_file = 'GDFL-' + foldername + '.html'
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
    Html_file.write(html_start)
    header = 'Folder structure for: ' + folder['name']
    html_heading = """
    <div style='text-align:center;'>
    <h1>""" + header + """</h1>
    </div>"""
    if (sys.version_info < (3, 0)):
        Html_file.write(html_heading.encode("utf-8"))
    else:
        Html_file.write(html_heading)
    html_list1 = """
    <UL id="example_tree" style="list-style: none;">
      <li><img src='https://ssl.gstatic.com/docs/doclist/images/icon_11_shared_collection_list_1.png'>
      <span>""" + folder['name'] + """</span>"""
    if (sys.version_info < (3, 0)):
        print('Building folder structure for {0}'.format(folder['name'].encode("utf-8")))
    else:
        print('Building folder structure for {0}'.format(folder['name']))

    get_folders(service, folder_id, level, Html_file, folders_only, drivetype)
    
    footer = ""
    if drivetype == 'Shared Drive':
        global FOLDERCOUNT
        global FILECOUNT
        global DEEPEST
        TOTALCOUNT = FOLDERCOUNT + FILECOUNT
        if folders_only == True:
            footer = """<h1>The number of folders = """ + str(FOLDERCOUNT) + """
                deepest nesting is """ + str(DEEPEST) + """</h1>"""
        else:
            footer = """<h1>The number of folders = """ + str(FOLDERCOUNT) + """
                and the number of files = """ + str(FILECOUNT) + """ 
                totalling: """ + str(TOTALCOUNT) + """
                deepest nesting is """ + str(DEEPEST) + """</h1>"""

    html_end = """
          </li>
        </ul>
        """ + footer + """
      </body>
    </html> """
    Html_file.write(html_end)
    Html_file.close()
    if (sys.version_info < (3, 0)):
        webbrowser.open(html_file.encode("utf-8"))
    else:
        webbrowser.open(html_file)

if __name__ == '__main__':
    main()
