from apiclient import discovery,errors
from httplib2 import Http
from oauth2client import client, file, tools
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
import os
from dotenv import load_dotenv

load_dotenv() 

FOLDER_ID = os.getenv('FOLDER_ID')
OUTPUT_DIR = os.getenv('OUTPUT_DIR')

if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
# define path variables
credentials_file_path = './credentials/credentials.json' #this file will be created by  google
clientsecret_file_path = './credentials/client_secret.json' #our credentials 

# define API scope
SCOPE = 'https://www.googleapis.com/auth/drive'

# define store
store = file.Storage(credentials_file_path)
credentials = store.get()
# get access token
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
    credentials = tools.run_flow(flow, store)

# define API service
http = credentials.authorize(Http())
drive = discovery.build('drive', 'v3', http=http)

# define a function to retrieve all files
def retrieve_all_files(api_service,folder):
    results = []
    page_token = folder

    while True:
        try:
            param = {}

            if page_token:
                param['q'] = "'{}' in parents".format(folder)

            files = api_service.files().list(**param).execute()
            # append the files from the current result page to our list
            results.extend(files.get('files'))
            # Google Drive API shows our files in multiple pages when the number of files exceed 100
            page_token = files.get('nextPageToken')

            if not page_token:
                break

        except errors.HttpError as error:
            print(f'An error has occurred: {error}')
            break
    # output the file metadata to console
    for file in results:
        print(file)

    return results

import io
import shutil
def file_download(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
        
    # Initialise a downloader object to download the file
    downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
    done = False

    try:
        # Download the data in chunks
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
            
        # Write the received data to the file
        with open(os.path.join(OUTPUT_DIR,file_name), 'wb') as f:
            shutil.copyfileobj(fh, f)

        print("File Downloaded")
        # Return True if file Downloaded successfully
        return True
    except:
        
        # Return False if something went wrong
        print("Something went wrong.")
        return False
# call the function
all_files = retrieve_all_files(drive,folder = FOLDER_ID)
for each in all_files:
    file_download(drive,each["id"],each["name"])