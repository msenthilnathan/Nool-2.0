import os
import sys
import tkinter as tk
# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_access import DataAccess
from ui import StudentStatusUI
from gdrive_handler import GDriveHandler
import xml.etree.ElementTree as ET



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

def connect_gdrive_and_download_students():
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
        gdrive_handler = GDriveHandler(credential_file, client_secrets_file)
        if(not gdrive_handler.connected):
            print('Connection failed. continue in offline mode...')
            return
       
        
        try:
            # Check if lock file exists
            if gdrive_handler.check_lock_file(folder_id, 'process.lock'):
                print('Resource is locked by someone else. Please wait.')
            else:
            
                current_directory = os.getcwd()
                print(f"Current working directory: {current_directory}")
        
                # Create a lock file
                print('Creating lock file...')
                gdrive_handler.create_lock_file(folder_id, 'process.lock')
            
                # Download the file as specified in the config
                local_path = os.path.join('data', file_name_to_download)
                print(f"Downloading the file... {local_path}")
                gdrive_handler.download_file(file_id_to_download, local_path)
            
                # Delete the lock file
                print('Deleting lock file...') 
                gdrive_handler.delete_lock_file(folder_id, 'process.lock')
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            # Ensure the lock file is deleted in case of an error
            gdrive_handler.delete_lock_file(folder_id, 'process.lock')

class MainApp:
    def __init__(self):
        students_file_name = 'students.xlsx'
        status_file_name = 'status.xlsx'
        
        # Get the parent directory of the current script (main_script.py)
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        
        self.students_file_path = os.path.join(parent_dir, 'data', students_file_name)
        self.status_file_path = os.path.join(parent_dir, 'data', status_file_name)
        self.config_file = os.path.join(parent_dir, 'config', 'config.xml')
        self.selected_student_id = None


        connect_gdrive_and_download_students()
        
        self.data_access = DataAccess(self.students_file_path, self.status_file_path,self.config_file)
        self.status_df = self.data_access.status_df
        self.students_df = self.data_access.students_df
        self.ui = StudentStatusUI(self.students_df,self.status_df,self.data_access)


    def run(self):
        self.ui.filter_displayed_student_list(None)
        self.ui.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
