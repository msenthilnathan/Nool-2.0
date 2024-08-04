import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from data_access import DataAccess


from src.SidePanelManager import SidePanelManager


class StudentStatusUI:
    def __init__(self,students_df, status_df,dataaccess):
        self.status_df = status_df
        self.students_df = students_df
        self.data_access = dataaccess
        self.setup_ui()
        

    def setup_ui(self):
        
        # Initialize the main application window
        self.root = tk.Tk()
        self.root.title("Nool 2.0 - Book Distribution System")
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(6, weight=1)  # Adjusted to 6 columns to accommodate scrollbars

        # Add a frame for the search bar
        search_frame = tk.Frame(self.root)
        search_frame.grid(row=0, column=0, columnspan=7, padx=10, pady=10, sticky="ew")

        # Add a label for the filter entry
        filter_label = tk.Label(search_frame, text="Search Students:", font=("Arial", 12))
        filter_label.grid(row=0, column=0, padx=(10, 5), pady=5)

        # Create a text box for filter entry
        self.filter_var = tk.StringVar()
        filter_entry = tk.Entry(search_frame, textvariable=self.filter_var, font=("Arial", 12))
        filter_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")

        # Set initial focus to the filter entry text box
        filter_entry.focus_set()

        # Create a treeview to display records
        columns = list(self.students_df.columns)
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            if(col == 'Parent Email Id'):
                self.tree.column(col, width=0, minwidth = 200 , stretch=True)  # Allow columns to stretch
            else:
                self.tree.column(col, width=0, minwidth = 120 , stretch=True)  # Allow columns to stretch
        self.tree.grid(row=1, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")

        # Add scrollbar to the treeview (vertical)
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=7, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        # Add scrollbar to the treeview (horizontal)
        hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=2, column=0, columnspan=7,  sticky='ew')
        self.tree.configure(xscrollcommand=hsb.set)


        # Style the treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#007acc", foreground="white")
        style.configure("Treeview", font=("Arial", 12), rowheight=25, background="white", foreground="black", fieldbackground="white")
        style.map("Treeview.Heading", background=[('active', '#005ea6')], foreground=[('active', 'white')])
        style.map("Treeview", background=[('selected', '#005ea6')], foreground=[('selected', 'white')])

        # Side panel to display selected record details
        details_frame = tk.Frame(self.root, bg="#f0f0f0")
        details_frame.grid(row=1, column=8, padx=10, pady=10, sticky="nsew")
        
        self.side_panel = SidePanelManager(details_frame,self.status_df,self.data_access)
        
        self.tree.bind("<<TreeviewSelect>>", self.display_student_list_and_side_panel)
        # Bind the filter entry to update the display
        self.filter_var.trace("w", self.filter_displayed_student_list)

            
        # Sync button
        self.sync_button = tk.Button(self.root, text="Sync", command=self.sync_status, font=("Arial", 12), bg="#f44336", fg="white")
        self.sync_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")  # Adjusted row and added pady for padding
            
        # Button to exit the application
        exit_button = tk.Button(self.root, text="Exit", command=lambda: self.root.quit(), font=("Arial", 12), bg="#f44336", fg="white")
        exit_button.grid(row=3, column=4, columnspan=3, padx=10, pady=10, sticky="ew")

        # Add a label below the Exit button
        label = tk.Label(self.root, text="  Inspired by the Nool Mobile app developed by Raj (rajmohan@hotmail.com)  ", font=("Arial", 12), background='#005ea6', foreground='white')
        label.grid(row=4, column=0, columnspan=7, padx=10, pady=10, sticky="ew")
  
    def display_student_list_and_side_panel(self,event):
        selected_item = self.tree.selection()
        if selected_item:
            record_values = self.tree.item(selected_item)["values"]
        else:
            # Display the first row if nothing is selected
            if len(self.tree.get_children()) > 0:
                first_item = self.tree.get_children()[0]
                self.tree.selection_set(first_item)
                record_values = self.tree.item(first_item)["values"]
            else:
                self.side_panel.clear_side_panel()
                return

        
        # Find the index of the 'Student ID' column
        for idx, column_name in enumerate(self.tree["columns"]):  # Assuming tree["columns"] gives you the column names
            if column_name == 'Student ID':
                selected_student_id = record_values[idx]
                break
        
        if selected_student_id:
            # Now you can use selected_student_id
            print(selected_student_id)
            self.side_panel.show_selected_student_details_on_side_panel(int(selected_student_id))
        
    # Function to update the displayed records based on filter
    def filter_displayed_student_list(self,*args):
        filter_text = self.filter_var.get().lower()
        filtered_df = self.students_df[self.students_df.apply(lambda row: row.astype(str).str.contains(filter_text, case=False).any(), axis=1)]
        
        # Clear existing items in the Treeview
        self.tree.delete(*self.tree.get_children())
        
        # Insert filtered data into Treeview with unique iid
        for i, row in filtered_df.iterrows():
            self.tree.insert("", "end", iid=i, values=list(row))
        
        # Select the first item if there is only one record
        if len(self.tree.get_children()) == 1:
            self.tree.selection_set(self.tree.get_children()[0])
        
        if not filtered_df.empty:
            self.display_student_list_and_side_panel(None)
        else:
            self.side_panel.clear_side_panel()
            
    #Function todownload status file from google drive
    #and merge with in memory copy data frame and local status.xlsx
    def sync_status(self):
        print("Sync called")
        self.data_access.sync_status()
    

    def show_message(self, message):
        messagebox.showinfo("Information", message) 
