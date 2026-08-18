import csv
import os
import re
import time
import cv2
import easyocr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import csvTopdf

# Initialize EasyOCR globally once (speeds up execution dramatically)
print("Initializing OCR Engine...")

# Setup Selenium Options
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

IMAGE_PATH = "captcha.png"

def image_to_text(path):
    reader = easyocr.Reader(['en'], gpu=False)
    img = cv2.imread(path)
    results = reader.readtext(img)
    if results:
        detected_text = "".join([res[1] for res in results])
        return re.sub(r"\D", "", detected_text)  # Keep only digits
    return ""

def collectDataAndStore(roll_number):
    try:
        rollNo = driver.find_element(By.CSS_SELECTOR, "span[id$='lblRollNo']").text.strip()
        cName = driver.find_element(By.CSS_SELECTOR, "span[id$='lblCName']").text.strip()
        fName = driver.find_element(By.CSS_SELECTOR, "span[id$='lblFName']").text.strip()
        marks = driver.find_element(By.CSS_SELECTOR, "span[id$='lblMarks']").text.strip()
        rank = driver.find_element(By.CSS_SELECTOR, "span[id$='lblRank']").text.strip()

        student_data = {
            "Roll No.": rollNo,
            "Candidate Name": cName,
            "Father's Name": fName,
            "Total Marks": marks,
            "Rank": rank
        }
        
        print(f"✅ Data Extracted for Roll {roll_number}: {student_data}")
        
        csv_file = "student_details.csv"
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=student_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(student_data)
        return True
    except Exception as e:
        print(f"⚠️ Extraction failed for Roll {roll_number}: {e}")
        return False

def extractCapture(i):
    # Ensure we are on the base page context
    if "ShowDetailedEntranceResult.aspx" in driver.current_url:
        try:
            driver.find_element(By.XPATH, "//input[@value='Back']").click()
            time.sleep(1)
        except:
            driver.get("https://results.puexam.in/ShowCurrentEntranceResult.aspx")

    if "ShowCurrentEntranceResult.aspx" not in driver.current_url:
        driver.get("https://results.puexam.in/ShowCurrentEntranceResult.aspx")
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "a#ctl00_LinkButton_Entrance").click()
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "a#ctl00_cph1_lbtn_PUM").click()
        time.sleep(1)

    # Retry loop context if CAPTCHA prediction fails
    success = False
    while not success:
        try:
            roll_no_input = driver.find_element(By.CSS_SELECTOR, "input#ctl00_cph1_txtRollNo")
            captcha_input = driver.find_element(By.CSS_SELECTOR, "input[id$='txtCapcha']")
            
            roll_no_input.clear()
            roll_no_input.send_keys(str(i))
            captcha_input.clear()
            time.sleep(1)
            # Screenshot CAPTCHA element
            if os.path.exists(IMAGE_PATH):
                os.remove(IMAGE_PATH)
            img_element = driver.find_element(By.XPATH, "//img[contains(@src,'CaptchaImage.axd')]")
            img_element.screenshot(IMAGE_PATH)
            time.sleep(0.5)
            
            # Predict text values
            capture = image_to_text(IMAGE_PATH)
            captcha_input.send_keys(capture)
            
            # Submit Form
            driver.find_element(By.CSS_SELECTOR, "input#ctl00_cph1_btnShowResult").click()
            time.sleep(2)
            
            # Check if navigation succeeded
            if "ShowDetailedEntranceResult.aspx" in driver.current_url:
                collectDataAndStore(i)
                # Safeguard cleanup for the file
                if os.path.exists(IMAGE_PATH):
                    os.remove(IMAGE_PATH)
                
                # Navigate Back to index structure safely
                driver.find_element(By.XPATH, "//input[@value='Back']").click()
                time.sleep(1.5)
                success = True
            else:
                # If page did not change, CAPTCHA was incorrect. Loop retries naturally.
                print(f"❌ CAPTCHA incorrect for Roll {i}. Retrying...")
        except Exception as loop_error:
            print(f"Inner process warning: {loop_error}. Resetting layout block...")
            driver.get("https://results.puexam.in/ShowCurrentEntranceResult.aspx")
            time.sleep(2)

def rankWiseArrang():
    # Read the CSV
    df = pd.read_csv("student_details.csv")

    # Make sure Rank is numeric
    df["Roll No"] = pd.to_numeric(df["Roll No"], errors="coerce")

    # Sort by Rank
    df = df.sort_values(by="Rank", ascending=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Save
    df.to_csv("student_details.csv", index=False)

    print("Sorted successfully!")

    
# --- Runtime Loop Process ---
try:
    if os.path.exists(IMAGE_PATH):
        os.remove(IMAGE_PATH)

    for i in range(150001,150010):
        print(f"\nProcessing student index: {i}...")
        extractCapture(i)

except Exception as e:
    print(f"\n❌ A critical error occurred during execution: {e}")

finally:
    rankWiseArrang()
    csvTopdf.convert_csv_to_pdf(csv_filename="student_details.csv", pdf_filename="student_details_sorted_with_branches.pdf")
    print("\nCleaning up web automation resources...")
    driver.quit()
    print("Browser completely closed.")