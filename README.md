# gdfl
Google Drive Folder List builds a html output file of a Google Drive folder.

This script will take an inoput folder ID or just run againnst the users Root if nothing specified.
The script get's the folder name by ID and then builds a sorted folder structure of all the child folders
and writes this structure to a html file which also contains collapsable folders and each folder is 
a link to the actual Google Drive folder

To be able to execute this script you will need to build a Google Developers project and a client_secret.json file
Follow these instructions:

1. Go to https://console.developers.google.com/start/api?id=drive to create or select a project in the Google Developers Console and automatically turn on the API. Click Continue, then Go to credentials.
2. On the Add credentials to your project page, click the Cancel button.
3. At the top of the page, select the OAuth consent screen tab. Select an Email address, enter a Product name if not already set, and click the Save button.
4. Select the Credentials tab, click the Create credentials button and select OAuth client ID.
5. Select the application type Other, enter the name "Drive API Quickstart", and click the Create button.
6. Click OK to dismiss the resulting dialog.
7. Click the file_download (Download JSON) button to the right of the client ID.
8. Move this file to your working directory and rename it client_secret.json.
9. Run the scritp using python gdfl.py -f FOLDER_ID
10. Authorise the script to have read only access to your Drive.
