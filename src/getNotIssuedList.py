import pandas as pd

# Step 1: Read the Excel files from the 'data' subfolder
students_df = pd.read_excel('data/students.xlsx', skiprows=1)
status_df = pd.read_excel('data/status.xlsx')

# Step 2: Print the column names to check for 'Student ID'
print("Students columns:", students_df.columns)
print("Status columns:", status_df.columns)

# Ensure 'Student ID' exists in both DataFrames
if 'Student ID' not in students_df.columns or 'Student ID' not in status_df.columns:
    raise KeyError("'Student ID' column is missing in one of the files")

# Step 3: Merge the DataFrames on 'Student ID' using a left join
merged_df = pd.merge(students_df, status_df[['Student ID', 'Books Given Status']], 
                     on='Student ID', how='left')

# Step 4: Fill missing 'Books Given Status' values with 'Not Given'
merged_df['Books Given Status'].fillna('Not Given', inplace=True)

# Step 5: Filter the DataFrame to exclude rows where 'Books Given Status' is 'All Given'
filtered_df = merged_df[merged_df['Books Given Status'] != 'All Given']

# Step 6: Display or save the filtered results
print(filtered_df)

# Optionally, save to a new Excel file in the same 'data' folder
filtered_df.to_excel('data/filtered_students.xlsx', index=False)
