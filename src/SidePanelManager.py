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
        self.original_details = {}
        self.create_widgets()
        #self.bind_variable_changes()

    def create_widgets(self):
        # Title
        self.title = tk.Label(self.master, text="Student Details", font=("Arial", 16))
        self.title.grid(row=0, columnspan=2)

        row = 1
        for label, var in self.details_vars.items():
            if label == 'Books Given Status':
                # Create radio buttons for Book Given Status
                var.set('Not Given')
                
                tk.Label(self.master, text=label).grid(row=row, column=0, sticky='w')
                self.not_given_radio = tk.Radiobutton(self.master, text='Not Given', variable=var, value='Not Given')
                self.not_given_radio.grid(row=row, column=1, sticky='w')
                row += 1

                self.all_given_radio = tk.Radiobutton(self.master, text='All Given', variable=var, value='All Given')
                self.all_given_radio.grid(row=row, column=1, sticky='w')
                row += 1

                self.partially_given_radio = tk.Radiobutton(self.master, text='Partially Given', variable=var, value='Partially Given')
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
        

    def bind_variable_changes(self):
        for var in self.details_vars.values():
            var.trace_add('write', self.check_for_changes)

    def check_for_changes(self, *args):
        current_details = {col: var.get() for col, var in self.details_vars.items()}
        if current_details != self.original_details:
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.NORMAL)
            #self.save_button.config(state=tk.DISABLED)

    def show_selected_student_details_on_side_panel(self, student_id):
        selected_row = self.status_df[self.status_df['Student ID'] == student_id]

        if selected_row.empty:
            print(f"No student found with ID {student_id}")
            for var in self.details_vars.values():
                var.set('')
        else:
            student_data = selected_row.squeeze()
            for col in self.details_vars:
                value = self.status_df.loc[self.status_df['Student ID'] == int(student_id),col].squeeze()
                # Check if the value is NaN and set the details_var accordingly
                if pd.isna(value):
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




    def save_details(self):
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
            self.data_access.save_status()
        elif books_given_status_from_entry != books_given_status_from_dataframe:
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Status'] = books_given_status_from_entry
            # Update the Date Given field with the current local time
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.details_vars['Books Given Date'].set(current_time)
            self.status_df.loc[self.status_df['Student ID'] == int(student_id),'Books Given Date'] =  current_time
            self.data_access.save_status()
        else:
            print("No change in status to save")



        # Disable the save button after saving
        #self.save_button.config(state=tk.DISABLED)

    
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
