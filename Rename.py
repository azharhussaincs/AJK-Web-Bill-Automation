import os
import pandas as pd
import glob

# Define paths
base_dir = "/home/azhar/Desktop/MobiserveTask/WebBilling"
pdf_dir = os.path.join(base_dir, "downloaded_bills")
excel_file = os.path.join(base_dir, "AJK Ref Number.xlsx")

# Load Excel: SiteID and Reference Number
df = pd.read_excel(excel_file, usecols=[1, 3])  # SiteID, ReferenceNo
df.columns = ["SiteID", "ReferenceNo"]
df["ReferenceNo"] = df["ReferenceNo"].astype(str).str.strip()

# Create a mapping from ReferenceNo to SiteID
ref_to_siteid = dict(zip(df["ReferenceNo"], df["SiteID"]))

# Get all PDF files in the download directory
pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))

renamed_count = 0
skipped_count = 0

for pdf_file in pdf_files:
    filename = os.path.basename(pdf_file)
    for ref_num in ref_to_siteid:
        if ref_num in filename:
            site_id = str(ref_to_siteid[ref_num]).strip()
            new_pdf_path = os.path.join(pdf_dir, f"{site_id}.pdf")

            if os.path.exists(new_pdf_path):
                print(f"⚠️ File already exists: {new_pdf_path} — skipping.")
                skipped_count += 1
                break

            os.rename(pdf_file, new_pdf_path)
            print(f"✅ Renamed: {filename} -> {site_id}.pdf")
            renamed_count += 1
            break
    else:
        print(f"❌ No matching reference number found in: {filename}")
        skipped_count += 1

print(f"\n🎉 Renaming complete: {renamed_count} files renamed, {skipped_count} skipped.")
