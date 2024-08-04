from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def authenticate():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    credentials_file = os.path.join(parent_dir, 'config', "mycreds.txt")
    gauth = GoogleAuth()
    
    # Load the client configuration from the credentials.json file
    gauth.LoadClientConfigFile(credentials_file)
  
    
    # Creates local webserver and auto handles authentication
    gauth.LocalWebserverAuth()
    
    return GoogleDrive(gauth)

def list_files_in_folder(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        print(f'title: {file["title"]}, id: {file["id"]}')
    return file_list

def download_file(drive, file_id, file_name):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(file_name)
    print(f'File {file_name} downloaded.')

def rename_file(drive, file_id, new_title):
    file = drive.CreateFile({'id': file_id})
    file['title'] = new_title
    file.Upload()
    file.FetchMetadata()
    print(f'File renamed to {file["title"]}.')

def upload_file(drive, local_file_path, parent_folder_id):
    file = drive.CreateFile({'title': os.path.basename(local_file_path), 'parents': [{'id': parent_folder_id}]})
    file.SetContentFile(local_file_path)
    file.Upload()
    print(f'File {local_file_path} uploaded to Drive.')

if __name__ == "__main__":
    # Authenticate and create the PyDrive client
    drive = authenticate()
    
    # Replace 'your_shared_folder_id' with the actual folder ID
    folder_id = '1hNUQxPSpsArumY0rR8BdcmwmXwHaRTSj'  # Replace with your shared folder ID
    
    # List files in the shared folder
    files = list_files_in_folder(drive, folder_id)
    
    if files:
        # Replace 'file_id_to_download' with the actual file ID you want to download
        #https://docs.google.com/spreadsheets/d/1xfdj2ieY3YnIkM9dDcolsBpSo8c-t7rP/edit?usp=drive_link&ouid=115505929929735977313&rtpof=true&sd=true
        file_id_to_download = '1xfdj2ieY3YnIkM9dDcolsBpSo8c-t7rP'
        file_name_to_download = 'test_from_gdrive.xlsx'
        download_file(drive, file_id_to_download, file_name_to_download)
        
        # Replace 'file_id_to_rename' with the actual file ID you want to rename
        file_id_to_rename = '1xfdj2ieY3YnIkM9dDcolsBpSo8c-t7rP'
        new_file_name = 'test_name_after_rename'  # Replace with the new name you want to give to the file
        rename_file(drive, file_id_to_rename, new_file_name)
        
        # Replace 'local_file_path' with the path of the local file you want to upload
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        test_file_to_upload = os.path.join(parent_dir, 'data', "status.xlsx")
        local_file_path = test_file_to_upload  # Replace with your local file path
        upload_file(drive, local_file_path, folder_id)
    else:
        print('No files found in the folder.')
