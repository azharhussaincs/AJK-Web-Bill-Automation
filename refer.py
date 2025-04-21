import os
import csv
from pdf2image import convert_from_path
import pytesseract
import re

# Folder containing the PDFs
pdf_folder = "/home/azhar/Desktop/MobiserveTask/WebBilling/downloaded_bills"

# Output CSV file path
csv_filename = os.path.join(pdf_folder, "units_consumed_data.csv")
failed_log_path = os.path.join(pdf_folder, "failed_renames.txt")

# Open CSV and log files
with open(csv_filename, mode="w", newline="") as file, open(failed_log_path, "w") as failed_log:
    writer = csv.writer(file)
    writer.writerow(["Site.ID", "UNITS CONSUMED", "REFERENCE NO"])

    # Loop through all PDF files
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.lower().endswith(".pdf"):
            site_id = os.path.splitext(pdf_file)[0]
            pdf_path = os.path.join(pdf_folder, pdf_file)

            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path)

                # Extract text from the first page
                text = pytesseract.image_to_string(images[0])

                # Extract "UNITS CONSUMED"
                match_units = re.search(r'UNITS CONSUMED\s+(\d+)', text)
                units_consumed = match_units.group(1) if match_units else "NULL"
                print(f"{site_id}: UNITS CONSUMED = {units_consumed}")

                # Extract "REFERENCE NO"
                reference_no = "NULL"
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if "REFERENCE NO" in line.upper():
                        for j in range(i, i + 3):  # Check current and next two lines
                            if j < len(lines):
                                match_ref = re.search(r'(\d{2}\s?\d{5}\s?\d{7})', lines[j])
                                if match_ref:
                                    reference_no = match_ref.group(1).replace(" ", "")  # Remove spaces
                                    print(f"{site_id}: REFERENCE NO = {reference_no}")
                                    break
                        break

                # Write to CSV
                writer.writerow([site_id, units_consumed, reference_no])

                # Rename PDF if reference number found
                if reference_no != "NULL":
                    new_pdf_name = f"{reference_no}.pdf"
                    new_pdf_path = os.path.join(pdf_folder, new_pdf_name)

                    if not os.path.exists(new_pdf_path):
                        os.rename(pdf_path, new_pdf_path)
                        print(f"Renamed '{pdf_file}' to '{new_pdf_name}'")
                    else:
                        print(f"File '{new_pdf_name}' already exists. Skipping rename.")
                        failed_log.write(f"{pdf_file} --> {new_pdf_name} [Already Exists]\n")
                else:
                    # Print full text for debugging
                    print(f"\n[DEBUG: REFERENCE NO not found for '{pdf_file}']\n{text}\n")
                    failed_log.write(f"{pdf_file} --> REFERENCE NO NOT FOUND\n")

            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
                failed_log.write(f"{pdf_file} --> ERROR: {e}\n")
