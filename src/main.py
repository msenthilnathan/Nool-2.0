import os
import sys
import tkinter as tk
from tkinter import messagebox

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_access import DataAccess
from ui import StudentStatusUI
from gdrive_handler import GDriveHandler
import xml.etree.ElementTree as ET


class MainApp:
    def __init__(self):
        students_file_name = 'students.xlsx'
        status_file_name = 'status.xlsx'
        
        self.students_file_path = os.path.join( 'data', students_file_name)
        self.status_file_path = os.path.join( 'data', status_file_name)
        self.config_file = os.path.join('config', 'config.xml')



    def run(self):
        
        # Change the current working directory to the parent directory of the src folder
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        os.chdir(parent_dir)
        
        if( not os.path.exists(self.students_file_path)  ):
            gdrive_handler = GDriveHandler()
            if(not gdrive_handler.connected):
                print("Gdrive not connected")
            else:
                gdrive_handler.download_students()
            
        if( not os.path.exists(self.students_file_path) ):
            messagebox.showerror("Nool 2.0 - Fatal Error: No Students list","Unable to find/download the Students list. Please connect to internet and try to download the list file")
            exit(-1)

        
        self.data_access = DataAccess(self.students_file_path, self.status_file_path,self.config_file)
        self.status_df = self.data_access.status_df
        self.students_df = self.data_access.students_df
        self.ui = StudentStatusUI(self.students_df,self.status_df,self.data_access)
        
        self.ui.filter_displayed_student_list(None)
        self.ui.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
