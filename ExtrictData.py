import os
import csv
from pdf2image import convert_from_path
import pytesseract
import re

# Get the current working directory (where PDFs are saved dynamically)
pdf_folder = "/home/azhar/Desktop/MobiserveTask/WebBilling/downloaded_bills"

# Output CSV file
csv_filename = os.path.join(pdf_folder, "units_consumed_data.csv")

# Open CSV file for writing
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Site.ID", "UNITS CONSUMED"])  # Updated column name

    # Loop through all PDF files in the folder
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):  # Process only PDF files
            site_id = os.path.splitext(pdf_file)[0]  # Remove .pdf extension
            pdf_path = os.path.join(pdf_folder, pdf_file)

            # Convert PDF to images
            images = convert_from_path(pdf_path)

            # Extract text from the first page
            text = pytesseract.image_to_string(images[0])

            # Find "UNITS CONSUMED" value using regex
            match = re.search(r'UNITS CONSUMED\s+(\d+)', text)

            if match:
                units_consumed = match.group(1)  # Extract number
                print(f"{site_id}: UNITS CONSUMED = {units_consumed}")
            else:
                units_consumed = "NULL"  # Fill missing values with NULL
                print(f"{site_id}: UNITS CONSUMED not found, setting to NULL")

            # Save data to CSV
            writer.writerow([site_id, units_consumed])
