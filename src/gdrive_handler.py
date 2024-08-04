import logging
import os
import socket
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import httplib2
from oauth2client.client import AccessTokenCredentials
from datetime import datetime, timezone



class GDriveHandler:
    def __init__(self, credential_file, client_secrets_file):
        try:
            self.credential_file = credential_file
            self.client_secrets_file = client_secrets_file
            self.setup_logging()
            self.drive = self.authenticate()
            self.connected = True
        except socket.gaierror:
            logging.error("Network error: Unable to resolve hostname. Please check your internet connection.")
            self.connected = False
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            self.connected = False

    def setup_logging(self):
        
        log_format = '%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
        # Configure logging
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'log'))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure info, trace, debug log
        info_trace_debug_logfile = os.path.join(log_dir, 'info_trace_debug.log')
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            filename=info_trace_debug_logfile,
                            filemode='a')
        
        # Configure errors, exceptions log
        errors_exceptions_logfile = os.path.join(log_dir, 'errors_exceptions.log')
        error_handler = logging.FileHandler(errors_exceptions_logfile)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger('').addHandler(error_handler)
        
        # Define a custom logging format




    def authenticate(self):
        try:
            gauth = GoogleAuth()
            gauth.settings['client_config_file'] = self.client_secrets_file
            
            # Try to load saved client credentials
            gauth.LoadCredentialsFile(self.credential_file)
            
            if gauth.credentials is None:
                # Authenticate if they're not there
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                try:
                    # Refresh them if expired
                    gauth.Refresh()
                except:
                    # If refresh fails, do a full authentication
                    gauth.LocalWebserverAuth()
            else:
                # Initialize the saved creds
                gauth.Authorize()
            
            
            # Save the current credentials to a file
            gauth.SaveCredentialsFile(self.credential_file)
            
            #self.get_user_info(gauth)

            
            drive = GoogleDrive(gauth)
            logging.info('Authentication successful.')
            return drive
        except Exception as e:
            logging.error(f'Authentication failed: {str(e)}')
            raise

    def get_user_info(self,gauth):
        # Extract credentials from GoogleAuth
        
        # Extract the access token from GoogleAuth
        access_token = gauth.credentials.access_token
        logging.info(f'Access token: {access_token}') 
        # Create credentials object using the access token
        credentials = AccessTokenCredentials(access_token, 'my-user-agent/1.0')

        # Build the OAuth2 service
        http = credentials.authorize(httplib2.Http())
        oauth2_service = build('oauth2', 'v2', http=http)
        
        

        # Get user info
        user_info = oauth2_service.userinfo().get().execute()

        # Print user details
        logging.info("User's Name: ", user_info['name'])
        logging.info("User's Email: ", user_info['email'])
        
    def list_files_in_folder(self, folder_id):
        file_list = self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        for file in file_list:
            logging.debug(f'title: {file["title"]}, id: {file["id"]}')
        return file_list

    def check_lock_file(self, folder_id, lock_file_name):
        query = f"'{folder_id}' in parents and title='{lock_file_name}' and trashed=false"
        file_list = self.drive.ListFile({'q': query}).GetList()
        return len(file_list) > 0

    def create_lock_file(self, folder_id, lock_file_name):
        lock_file = self.drive.CreateFile({'title': lock_file_name, 'parents': [{'id': folder_id}]})
        lock_file.SetContentString('Locked')
        lock_file.Upload()
        logging.info('Lock file created.')

    def delete_lock_file(self, folder_id, lock_file_name):
        query = f"'{folder_id}' in parents and title='{lock_file_name}' and trashed=false"
        file_list = self.drive.ListFile({'q': query}).GetList()
        for file in file_list:
            file.Delete()
        logging.info('Lock file deleted.')

    def download_file(self, file_id, file_name):
        file = self.drive.CreateFile({'id': file_id})
        file.GetContentFile(file_name)
        logging.info(f'File {file_name} downloaded.')
        
    

    def check_and_download_file(self, file_id, local_path):
        # Get local file modification time in UTC
        if os.path.exists(local_path):
            local_mod_time = datetime.fromtimestamp(os.path.getmtime(local_path), tz=timezone.utc)
            logging.info(f"Local file modification time (UTC): {local_mod_time}")
        else:
            logging.info(f"Local file {local_path} does not exist. Downloading the file.")
            local_mod_time = None

        # Get Google Drive file modification time (already in UTC)
        gdrive_file = self.drive.CreateFile({'id': file_id})
        gdrive_file.FetchMetadata(fields='modifiedDate')
        drive_mod_time_str = gdrive_file['modifiedDate']
        drive_mod_time = datetime.strptime(drive_mod_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
        logging.info(f"Google Drive file modification time (UTC): {drive_mod_time}")

        # Compare modification times and download if necessary
        if local_mod_time is None or drive_mod_time > local_mod_time:
            gdrive_file.GetContentFile(local_path)
            logging.info(f"Downloaded file from Google Drive to {local_path}.")
        else:
            logging.info(f"No need to download. The local file is up-to-date.")


    def rename_file(self, file_id, new_title):
        print(f"Going to rename the file as {new_title}")
        
        try:
            # Create a file instance with the given file_id
            file = self.drive.CreateFile({'id': file_id})
            file.FetchMetadata(fields='title')  # Fetch existing metadata
            logging.info(f'Original file name: {file["title"]}')

            # Update the title
            file['title'] = new_title
            file.Upload(param={'supportsAllDrives': True})  # Ensure supportsAllDrives is set if using shared drives

            # Fetch updated metadata to confirm the change
            file.FetchMetadata(fields='title')
            logging.info(f'File renamed to {file["title"]}.')
        except Exception as e:
            logging.error(f'An error occurred: {e}')

    def upload_file(self, local_file_path, parent_folder_id):
        file = self.drive.CreateFile({'title': os.path.basename(local_file_path), 'parents': [{'id': parent_folder_id}]})
        file.SetContentFile(local_file_path)
        file.Upload()
        logging.info(f'File {os.path.basename(local_file_path)} uploaded to Drive.')
