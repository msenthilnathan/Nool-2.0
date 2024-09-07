import pandas as pd

def check_and_merge(file1_path, file2_path, output_path):
    # Load both Excel files into DataFrames
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)

    # Ensure 'Student ID' is treated as a key for merging
    df1.set_index('Student ID', inplace=True)
    df2.set_index('Student ID', inplace=True)

    # Initialize an empty list to track conflicts
    conflicts = []

    # Iterate over each unique student ID from both files
    all_student_ids = sorted(set(df1.index).union(set(df2.index)))
    
    merged_rows = []

    for student_id in all_student_ids:
        row1 = df1.loc[student_id] if student_id in df1.index else None
        row2 = df2.loc[student_id] if student_id in df2.index else None
        
        # Handling logic for each case
        if row1 is not None and row2 is not None:
            # Compare 'Books Given Status'
            status1 = row1['Books Given Status']
            status2 = row2['Books Given Status']
            
            if pd.isna(status1) or status1 in ["Not Given", ""]:
                status1 = None
            if pd.isna(status2) or status2 in ["Not Given", ""]:
                status2 = None

            # Flag conflict only if both are non-empty and not the same, excluding 'Not Given'
            if status1 and status2 and status1 != status2:
                conflicts.append((student_id, row1, row2))
            else:
                # If only one is non-empty, choose the non-empty one
                if status1 is not None:
                    merged_rows.append(row1)
                else:
                   merged_rows.append(row2) 
        else:
            # If student exists only in one file, simply add their row
            final_row = row1 if row1 is not None else row2
            merged_rows.append(final_row)

    if conflicts:  # only print if there are conflicts
        print("Conflicts found with the following students:")
        for conflict in conflicts:
            print(conflict)
    else:
        print("No conflicts found. Merge can proceed.")
        merged_df = pd.DataFrame(merged_rows)
        merged_df.to_excel(output_path,index=True,index_label='Student ID')
        print(f"{output_path} written")



# Example usage:
file1_path = r'data\status_Suresh.xlsx'
file2_path = r'data\Yuvaraj status.xlsx'
file3_path = r'data\status_Surya.xlsx'
file4_path = r'data\Revathi status.xlsx'
output_path1 = r'data\merged_output1.xlsx'
output_path2 = r'data\merged_output2.xlsx'
output_path_final = r'data\merged_status.xlsx'



check_and_merge(file1_path, file2_path, output_path1)
check_and_merge(file3_path, file4_path, output_path2)
check_and_merge(output_path1, output_path2, output_path_final)


