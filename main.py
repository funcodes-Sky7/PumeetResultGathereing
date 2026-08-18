from PIL import Image
import cv2
import easyocr
import csv
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(
    options=options
)

def extractCapture(i):
    if driver.current_url !="https://results.puexam.in/ShowCurrentEntranceResult.aspx":
        driver.get("https://results.puexam.in/ShowCurrentEntranceResult.aspx")

        entrenceBtn = driver.find_element(By.CSS_SELECTOR, "a#ctl00_LinkButton_Entrance")
        
        entrenceBtn.click()

        time.sleep(1)
        pumeetBtn = driver.find_element(By.CSS_SELECTOR, "a#ctl00_cph1_lbtn_PUM")
        
        pumeetBtn.click()
        time.sleep(1)

    roll_no_input = driver.find_element(By.CSS_SELECTOR, "input#ctl00_cph1_txtRollNo")
    captcha_input = driver.find_element(By.CSS_SELECTOR, "input[id$='txtCapcha']")
    captcha_input.clear()
    roll_no_input.clear()
    roll_no_input.send_keys(i)
    time.sleep(1)
    img = driver.find_element(
    By.XPATH,
    "//img[contains(@src,'CaptchaImage.axd')]"
    )
    img.screenshot("captcha.png")
    time.sleep(1)
    capture = image_to_text("/Users/sundaramkumaryadav/Documents/MyMade/PythonFiles/resultGathering/captcha.png")
    captcha_input.send_keys(capture)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "input#ctl00_cph1_btnShowResult").click()
    if driver.current_url =="https://results.puexam.in/ShowDetailedEntranceResult.aspx":
        print("''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")
        time.sleep(3)
        collectDataAndStore(i)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "input#ctl00$cph1$btnBack").click()
    elif checkData() == i:
        os.remove(image_path)

        extractCapture(i)

def collectDataAndStore(i):
    # 3. Extract the text directly using the unique IDs from the HTML
    rollNo = driver.find_element(By.CSS_SELECTOR,"span[id$='lblRollNo']").text.strip()
    time.sleep(0.5)
    cName = driver.find_element(By.CSS_SELECTOR,"span[id$='lblCName']").text.strip()
    time.sleep(0.5)

    fName = driver.find_element(By.CSS_SELECTOR,"span[id$='lblFName']").text.strip()
    time.sleep(0.5)

    marks = driver.find_element(By.CSS_SELECTOR,"span[id$='lblMarks']").text.strip()
    time.sleep(0.5)

    rank = driver.find_element(By.CSS_SELECTOR,"span[id$='lblRank']").text.strip()
    time.sleep(0.5)

    student_data = {
        "Roll No.": rollNo,
        "Candidate Name": cName,
        "Father's Name": fName,
        "Total Marks": marks,
        "Rank": rank
    }
    
    print("Successfully Extracted Data:", student_data)
    
    # 4. Save/Append data to CSV file
    csv_file = "student_details.csv"
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=student_data.keys())
        # Write the header only if the file is new
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(student_data)
        print("Data successfully saved to student_details.csv!")

def checkData():
    with open("student_details.csv", mode="r", encoding="utf-8") as f:
        # Subtract 1 to account for the header row
        row_count = sum(1 for row in f)
        return row_count
    
def image_to_text(image_path):

    reader = easyocr.Reader(['en'], gpu=False) # Set gpu=True if you have a CUDA-enabled GPU

    # Read the image using OpenCV
    img = cv2.imread(image_path)
    
    # Run the reader on the image
    results = reader.readtext(img)
    
    # Print out everything found to see what's happening
    print("Full OCR Results:", results)
    
    # Extract just the text string from the results
    if results:
        # results looks like: [([[bbox]], 'text', confidence_score)]
        detected_text = "".join([res[1] for res in results])
        # Strip out any unintended spaces
        return re.sub(r"\D", "", detected_text)
    
    return "No text detected"

image_path = "captcha.png" 
if os.path.exists(image_path):
    os.remove(image_path)
    print(f"Successfully deleted: {image_path}")
else:
    print(f"The file {image_path} does not exist.")

for i in range(150001,150296):
    try: 
        extractCapture(i)
    except Exception as e:
    # 3. This block runs ONLY if an error/exception occurs
        print(f"\n❌ An error occurred during execution: {e}")
    # finally:
    # # 4. This block ALWAYS runs, even if the script crashed above
    #     print("\nCleaning up resources...")
    #     if 'driver' in locals():
    #         driver.quit()  # Closes ALL browser windows and kills the driver session safely
    #         print("Browser closed and driver quit successfully.")
# text_result = image_to_text(image_file)

# print("--- Extracted Text ---")
# print(text_result)
