import xml.etree.ElementTree as ET
import os
import logging
from gdrive_handler import GDriveHandler

def read_config(config_file):
    tree = ET.parse(config_file)
    root = tree.getroot()
    
    config = {
        'folder_id': root.find('folder_id').text,
        'file_id_to_download': root.find('file_id_to_download').text,
        'file_name_to_download': root.find('file_name_to_download').text,
        'file_id_to_rename': root.find('file_id_to_rename').text,
        'new_file_name': root.find('new_file_name').text,
        'test_file_to_upload': root.find('test_file_to_upload').text
    }
    
    return config

if __name__ == "__main__":
    
  
    # Define paths
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    
    # Change the current working directory to the parent directory
    os.chdir(parent_dir)
    
    
    config_file = os.path.join(parent_dir, 'config', 'gdrive_test_properties.xml')
    credential_file = os.path.join(parent_dir, 'config', 'mycreds.txt')
    client_secrets_file = os.path.join(parent_dir, 'config', 'client_secrets.json')
    
    # Read configuration from the XML file
    config = read_config(config_file)
    
    folder_id = config['folder_id']
    file_id_to_download = config['file_id_to_download']
    file_name_to_download = config['file_name_to_download']
    file_id_to_rename = config['file_id_to_rename']
    new_file_name = config['new_file_name']
    test_file_to_upload = os.path.join(parent_dir, 'data', config['test_file_to_upload'])
    
    # Initialize the GDriveHandler with the credentials file and client secrets
    gdrive_handler = GDriveHandler(credential_file, client_secrets_file)
    if(not gdrive_handler.connected):
        print('Connection failed. Exiting...')
        exit(1)
    
    try:
        print('Starting the process...')
        # Check if lock file exists
        if gdrive_handler.check_lock_file(folder_id, 'process.lock'):
            logging.info('Resource is locked by someone else. Please wait.')
        else:
            
            current_directory = os.getcwd()
            print(f"Current working directory: {current_directory}")
        
            # Create a lock file
            print('Creating lock file...')
            gdrive_handler.create_lock_file(folder_id, 'process.lock')
            
            # Download the file as specified in the config
            print(f"Downloading the file... {file_name_to_download}")
            gdrive_handler.download_file(file_id_to_download, file_name_to_download)
            
            # check and download the file as specified in the config
            print(f"Check and download the file... {file_name_to_download}")
            gdrive_handler.check_and_download_file(file_id_to_download, file_name_to_download)
            
            # Rename the file as specified in the config
            print(f"Renaming the file to... {new_file_name}")  
            gdrive_handler.rename_file(file_id_to_rename, new_file_name)
            
            # Upload a local file as specified in the config
            print("Uploading the file... ") 
            gdrive_handler.upload_file(test_file_to_upload, folder_id)
            
            # Delete the lock file
            print('Deleting lock file...') 
            gdrive_handler.delete_lock_file(folder_id, 'process.lock')
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        logging.error(f'An error occurred: {str(e)}', exc_info=True)
        # Ensure the lock file is deleted in case of an error
        gdrive_handler.delete_lock_file(folder_id, 'process.lock')
    print('Process completed.')
    input('Press any key to continue...')
    
