import pandas as pd
import glob

folder_path = './compair'

# Get all CSV files in the specified folder
csv_files = glob.glob(f'{folder_path}/*.csv')

# Initialize empty DataFrames to store data
df1 = None
df2 = None

# Read the files into DataFrames
for file_name in csv_files:
    print(f"Reading file: {file_name}")
    
    df = pd.read_csv(file_name)
    
    if 'Site.ID' in df.columns:
        if 'Ref No' in df.columns:  # Check if Ref No exists
            if df1 is None:
                df1 = df[['Site.ID', 'Ref No']]  # Store Site.ID and Ref No from the first file
            else:
                df2 = df[['Site.ID', 'Ref No']]  # Store Site.ID and Ref No from the second file
        else:
            if df1 is None:
                df1 = df[['Site.ID']]  # Only Site.ID if Ref No is missing
            else:
                df2 = df[['Site.ID']]  # Only Site.ID if Ref No is missing

# Check if both DataFrames are present
if df1 is not None and df2 is not None:
    # Find Site.ID values that are missing in each file
    missing_in_file1 = df2[~df2['Site.ID'].isin(df1['Site.ID'])]
    missing_in_file2 = df1[~df1['Site.ID'].isin(df2['Site.ID'])]

    # Add corresponding 'Ref No' from the other file
    missing_in_file1_ref = pd.merge(missing_in_file1, df1, on='Site.ID', how='left')
    missing_in_file2_ref = pd.merge(missing_in_file2, df2, on='Site.ID', how='left')

    # Combine missing data with 'Ref No'
    missing_data = pd.concat([missing_in_file1_ref, missing_in_file2_ref], ignore_index=True)

    # Save missing data to a new CSV file
    missing_data.to_csv('./compair/missing_site_ids_with_ref.csv', index=False)

    print(f"Missing Site.ID and corresponding Ref No saved to './compair/missing_site_ids_with_ref.csv'")
else:
    print("Not enough data to compare or missing Site.ID column in one of the files.")
