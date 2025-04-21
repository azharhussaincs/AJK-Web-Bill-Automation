import pandas as pd
import os

def compare_and_save_missing_refs(excel_file, csv_file, output_txt):
    try:
        # Load reference numbers from Excel file
        print(f"📄 Reading reference numbers from Excel: {excel_file}")
        df_excel = pd.read_excel(excel_file)
        excel_refs = set(str(row.iloc[3]).strip() for _, row in df_excel.iterrows())

        # Load reference numbers from CSV file
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return

        print(f"📄 Reading reference numbers from CSV: {csv_file}")
        df_csv = pd.read_csv(csv_file)

        if "REFERENCE NO" not in df_csv.columns:
            print("❌ 'REFERENCE NO' column not found in CSV.")
            print(f"🧾 Available columns: {list(df_csv.columns)}")
            return

        csv_refs = set(str(ref).strip() for ref in df_csv["REFERENCE NO"])

        # Compare to find missing reference numbers
        missing_refs = excel_refs - csv_refs

        # Write missing ones to txt file
        if missing_refs:
            with open(output_txt, "w") as f:
                for ref in sorted(missing_refs):
                    f.write(ref + "\n")
            print(f"📝 Missing reference numbers written to '{output_txt}'")
        else:
            print("✅ All reference numbers from Excel are present in the CSV.")

    except Exception as e:
        print(f"⚠️ Error during comparison: {e}")

# File paths
excel_file = "AJK Ref Number.xlsx"
csv_file = "/home/azhar/Desktop/MobiserveTask/WebBilling/downloaded_bills/units_consumed_data.csv"
output_txt = "missing_references.txt"

# Run the comparison
compare_and_save_missing_refs(excel_file, csv_file, output_txt)
