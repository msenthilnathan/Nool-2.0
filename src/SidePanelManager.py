import tkinter as tk
import pandas as pd
from datetime import datetime
from src.data_access import DataAccess

class SidePanelManager:
    def __init__(self, master, status_df, dataaccess:DataAccess):
        self.master = master
        self.status_df = status_df
        self.data_access = dataaccess
        self.details_vars = {col: tk.StringVar() for col in status_df.columns}
        self.current_student_id=''
        self.current_radio_value=tk.StringVar(value="")
        self.old_radio_value=tk.StringVar(value="")
        self.create_widgets()
        self.bind_variable_changes()
        self.data_changed = False


    def create_widgets(self):
        # Title
        self.title = tk.Label(self.master, text="Student Details", font=("Arial", 16))
        self.title.grid(row=0, columnspan=2)

        row = 1
        for label, var in self.details_vars.items():
            if label == 'Books Given Status':
                # Create radio buttons for Book Given Status
                
                tk.Label(self.master, text=label).grid(row=row, column=0, sticky='w')
                self.not_given_radio = tk.Radiobutton(self.master, text='Not Given', variable=self.current_radio_value, value='Not Given')
                self.not_given_radio.grid(row=row, column=1, sticky='w')
                row += 1

                self.all_given_radio = tk.Radiobutton(self.master, text='All Given', variable=self.current_radio_value, value='All Given')
                self.all_given_radio.grid(row=row, column=1, sticky='w')
                row += 1

                self.partially_given_radio = tk.Radiobutton(self.master, text='Partially Given', variable=self.current_radio_value, value='Partially Given')
                self.partially_given_radio.grid(row=row, column=1, sticky='w')
                row += 1
            else:
                tk.Label(self.master, text=label).grid(row=row, column=0, sticky='w')
                tk.Entry(self.master, textvariable=var, state='readonly').grid(row=row, column=1)
                row += 1
                

        # Save button
        self.save_button = tk.Button(self.master, text="Save", command=self.save_details)
        self.save_button.grid(row=row, columnspan=2, pady=10)  # Adjusted row and added pady for padding
        #self.save_button.config(state=tk.DISABLED)
        row += 1
        
        # Create a label to show the total number of students
        self.stats_student_count = tk.Label(self.master, text=f"Total number of students: {len(self.data_access.students_df)}")
        self.stats_student_count.grid(row=row, columnspan=5, pady=10)  # Adjusted row and added pady for padding
        row += 1
        
        # Calculate and display the count of 'All Given' statuses
        all_given_count = self.status_df[self.status_df['Books Given Status'] == 'All Given'].shape[0]
        self.status_count_label = tk.Label(self.master, text=f"Number of students with status 'All Given': {all_given_count}")
        self.status_count_label.grid(row=row, columnspan=5, pady=10)  # Adjusted row and added pady for padding
        row += 1
        

    def bind_variable_changes(self):
        #for var in self.details_vars.values():
        self.current_radio_value.trace_add('write', self.onRadioButtonSelect)

    def onRadioButtonSelect(self, *args):
        if self.isFirstTime == True:
            #print(f"Initializing the side panel from global status. No need to update radio selection")
            return
        

        print(f"StudentID:{self.current_student_id}; Button Selected:{self.current_radio_value.get()}; Old button: {self.old_radio_value.get()}")
        if self.current_radio_value.get() == self.old_radio_value.get():
            print(f"No button change")
            return
            
        self.data_changed = True
        if self.current_radio_value.get() == "Not Given" :
            self.details_vars['Books Given Status'].set('Not Given')
            self.details_vars['Books Given Date'].set("")
            self.details_vars['Grade Given'].set("")
            return
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_grade = self.data_access.students_df.loc[self.data_access.students_df['Student ID'] == int(self.current_student_id), 'Grade Name'].values[0]

        self.details_vars['Books Given Status'].set(self.current_radio_value.get())
        self.details_vars['Books Given Date'].set(current_time)
        self.details_vars['Grade Given'].set(current_grade)
        
        self.save_button.config(state=tk.NORMAL)
            #self.save_button.config(state=tk.DISABLED)

    def show_selected_student_details_on_side_panel(self, student_id):
        if self.current_student_id != '' and  self.current_student_id != student_id and self.data_changed:
            print(f"Auto saving {self.current_student_id}")
            self.save_details()
            
        self.current_student_id=student_id
        self.isFirstTime = True

        selected_row = self.status_df[self.status_df['Student ID'] == student_id]
        self.current_radio_button='Not Given'
        if selected_row.empty:
            print(f"No status found with ID {student_id}. Initialize it")
            self.status_df = self.data_access.initStatusForAStudent(student_id)
            
            selected_row = self.status_df[self.status_df['Student ID'] == int(student_id)]
            if selected_row.empty:
                print(f"Fatal: Still not found")
                selected_row = self.data_access.status_df[self.data_access.status_df['Student ID'] == int(student_id)]
                if selected_row.empty:
                    print(f"Fatal 2: Still not found")
        #else:
            #print(f"status found with ID {student_id}.");
        student_data = selected_row.squeeze()
        for col in self.details_vars:
            value = self.status_df.loc[self.status_df['Student ID'] == int(student_id),col].squeeze()
            # Check if the value is NaN and set the details_var accordingly
            #print(f"Check column:{col}={value}")
            if col != 'Student ID' and pd.isna(value) :
                self.details_vars[col].set('')
            else:
                self.details_vars[col].set(str(value))
            
        if student_data['Books Given Status'] == 'All Given':
            self.details_vars['Books Given Status'].set('All Given')
            self.all_given_radio.select()
        elif student_data['Books Given Status'] == 'Partially Given':
            self.details_vars['Books Given Status'].set('Partially Given')
            self.partially_given_radio.select()
        else:
            self.details_vars['Books Given Status'].set('Not Given')
            self.not_given_radio.select()
            
            
        self.isFirstTime = False


    def save_details(self):
        
        if not self.data_changed:
            print(f"No change in data")

        # Retrieve the current values from the detail fields
        entry_details = {col: var.get() for col, var in self.details_vars.items()}
        student_id = entry_details['Student ID']
        books_given_status_from_entry=entry_details['Books Given Status']
        books_given_date_from_entry=entry_details['Books Given Date']

        books_given_status_from_dataframe = str(self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Status'].squeeze())
        books_given_date_from_dataframe = str(self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Date'].squeeze())

        if pd.isna(books_given_status_from_entry):
            books_given_status_from_entry="Not Given"
        if pd.isna(books_given_status_from_dataframe):
            books_given_status_from_dataframe="Not Given"
        if books_given_status_from_entry == "Not Given" :
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Date'] =  ''
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Status'] = books_given_status_from_entry
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Grade Given'] = entry_details['Grade Given'];

            self.data_access.save_status()
            self.update_status_count()
            self.data_changed=False
            print(f"Changes saved")


        elif books_given_status_from_entry != books_given_status_from_dataframe:
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Status'] = books_given_status_from_entry
            if pd.isna(books_given_date_from_entry):
                # Update the Date Given field with the current local time
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.details_vars['Books Given Date'].set(current_time)
            else:
                current_time = books_given_date_from_entry
    
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Date'] =  current_time
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Grade Given'] = entry_details['Grade Given'];
            self.data_access.save_status()
            self.data_changed=False
            self.update_status_count()
            print(f"Changes saved")
        else:
            print("No change in status to save")
        

    def update_status_count(self):
        """Updates the label displaying the count of 'All Given' statuses."""
        all_given_count = self.status_df[self.status_df['Books Given Status'] == 'All Given'].shape[0]
        self.status_count_label.config(text=f"Number of students with status 'All Given': {all_given_count}")


    #Function to clear the side panel
    def clear_side_panel(self):
        for col in self.status_df.columns:
            self.details_vars[col].set("")
# Example usage
if __name__ == "__main__":
    # Sample data with a missing 'Grade' for student ID 3
    data = {
        'Student ID': [1, 2, 3],
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Grade': ['A', 'B', pd.NA],  # Grade for Charlie is missing (NaN)
        'Status': ['Pass', 'Pass', 'Fail'],
        'Date Given': [pd.NA, pd.NA, pd.NA],  # Date Given field
        'Book Given Status': ['Not Given', 'All Given', 'Partially Given']
    }
    df = pd.DataFrame(data)

    root = tk.Tk()
    dataaccess = DataAccess()
    panel = SidePanelManager(root, df,dataaccess)

    # Display details for student with ID 3
    panel.show_selected_student_details_on_side_panel(3)

    root.mainloop()
