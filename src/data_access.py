import pandas as pd
import xml.etree.ElementTree as ET
import openpyxl
import os
from datetime import datetime
import pytz
from tzlocal import get_localzone


class DataAccess:
    def __init__(self, students_file, status_file, config_file):
        self.students_file = students_file
        self.status_file = status_file
        self.config_file = config_file
        self.allowed_columns = self.parse_allowed_columns(config_file)
        print("Editable Columns from config.xml:", self.allowed_columns)
        self.skiprows = self.get_skiprows_from_config(config_file)
        self.usecols = self.get_usecolumns_from_config(config_file)
        print(f"Skip rows: {self.skiprows}")
        print(f"Use columns: {self.usecols}")
        self.students_df = self.read_students_data()
        self.status_df = self.read_status_data()
                

    #read student excel file - use the useCols and skip skipRows from the config file
    def read_students_data(self):
        if not os.path.exists(self.students_file):
            raise FileNotFoundError(f"{self.students_file} not found")
        print(f"Reading Excel file: {self.students_file}")
        try:
            students_df = pd.read_excel(self.students_file, skiprows=self.skiprows, usecols=self.usecols)[self.usecols]
            print(f"First few students read:{students_df.head()}")
        except Exception as e:
            print("Error reading Excel file with parameters:", e)
            students_df = pd.read_excel(self.students_file)
        return students_df
    
    def save_status(self):
        self.status_df.to_excel(self.status_file,index=False)

    def parse_allowed_columns(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        allowed_columns = [column_elem.attrib.get('name', '') for column_elem in root.findall('.//column') if column_elem.attrib.get('name', '')]
        return allowed_columns

    def get_filtered_columns_list(self):
        wb = openpyxl.load_workbook(self.students_file)
        sheet = wb.active
        header_row = next(sheet.iter_rows(min_row=2, max_row=2, values_only=True))
        wb.close()
        return [col for col in header_row if col in self.allowed_columns]

    def get_skiprows_from_config(self, config_file):
        tree = ET.parse(config_file)
        root = tree.getroot()
        skiprows_element = root.find('skiprows')
        return int(skiprows_element.text) if skiprows_element is not None and skiprows_element.text else 1

    def get_usecolumns_from_config(self, config_file):
        tree = ET.parse(config_file)
        root = tree.getroot()
        columns_element = root.find('usecolumns')
        if columns_element is not None and columns_element.text:
            usecols = [col.strip() for col in columns_element.text.split(',')]
        else:
            usecols = []
        return usecols

    def read_status_data(self):
        if os.path.exists(self.status_file): 
            try:    
                self.status_df = pd.read_excel(self.status_file)
                print("First 5 rows of the input status file with parameters:\n", self.status_df.head())
            except Exception as e:
                print("Error reading status file with parameters:", e)
                print(f"First 5 rows of the input Excel file without parameters:\n", self.status_df.head())
        else:
            print(f"File {self.status_file} not found.")
            self.status_df = self.students_df[['Student ID', 'Student First Name', 'Student Last Name']]
            self.status_df['Grade Given'] = ''
            self.status_df['Books Given Date'] = ''
            self.status_df['Books Given Status'] = ''
            print(f"After status initialized:{self.status_df}")

                
    
        return self.status_df

    def initStatusForAStudent(self,student_id):
        print(f"Before update status_df:{self.status_df}")

        new_row = {
            'Student ID': int(student_id),
            'Student First Name': self.students_df.loc[self.students_df['Student ID'] == int(student_id),'Student First Name'].values[0],
            'Student Last Name': self.students_df.loc[self.students_df['Student ID'] == int(student_id),'Student Last Name'].values[0],
            'Grade Given': '',
            'Books Given Date': '',
            'Books Given Status' : ''
            }
        new_row_df = pd.DataFrame([new_row])

        self.status_df = pd.concat([self.status_df, new_row_df], ignore_index=True)
        print(f"Updated status_df:{self.status_df}")
        return self.status_df


    def update_status(self, selected_student_id, details_vars):
        print(f"Updating status for student ID: {selected_student_id}")
        selected_student_id = int(selected_student_id)
        for col, var in details_vars.items():
            value = var.get()
            print(f"Updating {col} with value: {value}") 
            # Explicitly cast to the correct type based on the column dtype
            if col == 'Student ID':
                value = int(value)  # Assuming 'Student ID' should be an integer
            else:
                if self.status_df[col].dtype == 'int64':
                    value = int(value)
                elif self.status_df[col].dtype == 'float64':
                    value = float(value)
                else:
                    value = str(value)
            if col == 'BooksGivenDate' and value == '':
                current_utc_dt = datetime.utcnow()

                # Convert UTC to local timezone (assuming local timezone is 'Asia/Kolkata')
                local_tz = get_localzone()
                current_local_dt = current_utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

                # Format datetime as text for display
                formatted_datetime = current_local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
                value = formatted_datetime
            # Update details_vars with the new  value
            var.set(value)
            self.status_df.loc[self.status_df['Student ID'] == selected_student_id, col] = value
            # Print only the updated record of selected_student_id
            updated_record = self.status_df[self.status_df['Student ID'] == selected_student_id]
            print(f"Updated record for student ID {selected_student_id}:\n{updated_record}")
           
        return self.status_df
    
    
    def sync_status(self):
        print("Data access sync called")