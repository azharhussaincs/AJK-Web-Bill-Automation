import shutil
import os
import time
import glob
import pandas as pd
import subprocess
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define strict project directory for downloads
project_dir = os.path.abspath("downloaded_bills")

# Clear the folder if it's not empty
if os.path.exists(project_dir) and os.listdir(project_dir):
    print("❗ Clearing the 'downloaded_bills' folder...")
    shutil.rmtree(project_dir)  # Delete the folder and its contents
    os.makedirs(project_dir)  # Recreate the folder

os.makedirs(project_dir, exist_ok=True)

# Set up Chrome options
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--kiosk-printing")  # Forces automatic printing

    prefs = {
        "download.default_directory": project_dir,
        "savefile.default_directory": project_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True  # Avoids opening PDFs in browser
    }
    chrome_options.add_experimental_option("prefs", prefs)
    return chrome_options

# Set up ChromeDriver path
chrome_driver_path = os.path.join(os.getcwd(), "chromedriver-linux64", "chromedriver")

# 🔄 Load and combine all .xlsx files
print("📂 Loading all Excel files...")
excel_files = glob.glob("*.xlsx")
df_list = [pd.read_excel(file) for file in excel_files]
df = pd.concat(df_list, ignore_index=True)
print(f"✅ Loaded {len(excel_files)} Excel file(s), total records: {len(df)}")

def get_latest_file(download_path, timeout=30):
    """Waits for the most recent file in the download directory."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = glob.glob(os.path.join(download_path, "*.pdf"))
        if files:
            latest_file = max(files, key=os.path.getctime)  # Get the most recent file
            if "AJK ONLINE BILL" in latest_file:
                return latest_file
        time.sleep(1)
    return None

def download_bill(ref_number):
    """Downloads the bill for a given reference number in a separate Chrome instance."""
    try:
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=get_chrome_options())

        # Open the billing website
        driver.get("https://bill.pitc.com.pk/iescobill")
        time.sleep(2)

        # Find search input and button
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="searchTextBox"]'))
        )
        search_button = driver.find_element(By.XPATH, '//*[@id="btnSearch"]')

        # Input reference number and search
        search_box.clear()
        search_box.send_keys(ref_number)
        time.sleep(1)
        search_button.click()
        time.sleep(2)

        # Click print button
        print_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="printBtn"]/button'))
        )
        print_button.click()
        time.sleep(3)

        # Click final print button
        final_print_button_xpath = "/html/body/print-preview-app//print-preview-sidebar//print-preview-button-strip//div/cr-button[2]"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, final_print_button_xpath))
        ).click()

        # Wait for bill to be downloaded
        downloaded_file = get_latest_file(project_dir)

        if downloaded_file:
            print(f"📥 Download complete: {downloaded_file}")
        else:
            print(f"❌ Error: Download failed for Reference {ref_number}")

    except Exception as e:
        print(f"❌ Error processing Reference {ref_number}: {e}")

    finally:
        driver.quit()

# Process in batches of 
batch_size = 10
reference_numbers = [str(row.iloc[3]).strip() for _, row in df.iterrows()]

with ThreadPoolExecutor(max_workers=batch_size) as executor:
    for i in range(0, len(reference_numbers), batch_size):
        batch = reference_numbers[i:i + batch_size]
        executor.map(download_bill, batch)

print("\n🎉 All bills downloaded successfully!")

# Run the Rename.py script after completing the downloads
# rename_script = os.path.join(os.getcwd(), "Rename.py")
# subprocess.run(["python3", rename_script])

print("\n✅ Rename.py executed successfully!")

# Run ExtractData.py
# unit_consumed = os.path.join(os.getcwd(), "ExtrictData.py")
# subprocess.run(["python3", unit_consumed])

print("\n✅ ExtractData.py executed successfully!")
