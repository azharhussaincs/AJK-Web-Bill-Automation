import os
import pandas as pd
import time
import glob

# Define paths
base_dir = "/home/azhar/Desktop/MobiserveTask/WebBilling"
pdf_dir = os.path.join(base_dir, "downloaded_bills")
excel_file = os.path.join(base_dir, "AJK Ref Number.xlsx")

# Load the Excel file
df = pd.read_excel(excel_file, usecols=[1, 3])  # Site ID and Reference Number columns
df.columns = ["SiteID", "ReferenceNo"]
df["ReferenceNo"] = df["ReferenceNo"].astype(str).str.strip()

# Get all PDF files sorted by creation time (oldest first)
def get_all_pdfs():
    pdf_files = glob.glob(os.path.join(pdf_dir, "AJK ONLINE BILL*.pdf"))
    return sorted(pdf_files, key=os.path.getctime)  # Sort in the correct order

# Function to rename each bill correctly
def rename_bills():
    pdf_files = get_all_pdfs()
    
    if len(pdf_files) < len(df):
        print(f"⚠️ Warning: {len(pdf_files)} PDFs found, but {len(df)} Site IDs exist!")
        print("⚠️ Some bills may be missing or still downloading.")

    for i, pdf_file in enumerate(pdf_files):
        if i >= len(df):
            print(f"❌ Skipping extra file: {pdf_file}")
            continue

        site_id = str(df.iloc[i]["SiteID"]).strip()  # Get corresponding Site ID
        new_name = os.path.join(pdf_dir, f"{site_id}.pdf")

        if os.path.exists(new_name):  # Avoid overwriting
            print(f"⚠️ File '{new_name}' already exists. Skipping renaming.")
            continue

        os.rename(pdf_file, new_name)
        print(f"✅ Renamed: {pdf_file} -> {new_name}")
        time.sleep(1)  # Small delay for stability

# Start renaming process
rename_bills()

print("\n🎉 All applicable files renamed successfully!")

