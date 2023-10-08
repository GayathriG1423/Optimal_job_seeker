# Open File in read binary mode
import PyPDF2
import openai
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Replace the line where you set the webdriver_path with the following:

driver = webdriver.Chrome(ChromeDriverManager().install())

# The rest of your code remains unchanged

api_key = 'your_api_key'
openai.api_key = api_key
file = open("resume_test.pdf", "rb")

# pass the file object to PdfReader
pdf_reader = PyPDF2.PdfReader(file)

# numPages will return the number of pages in pdf
num_pages = len(pdf_reader.pages)
print("Number of pages in the PDF:", num_pages)

# Initialize an empty string to store all the extracted text
all_pdf_text = ""

# Iterate through all pages and extract text
for page in pdf_reader.pages:
    page_text = page.extract_text()
    all_pdf_text += page_text

# Print the combined text from all pages
print(all_pdf_text)

# Close the file when done
file.close()

# Assuming you have extracted text in the variable 'all_pdf_text'

# Define the prompt to send to GPT-3 based on the extracted text
prompt = f"I have extracted the following text from a PDF:\n{all_pdf_text}\n\nSuggest suitable job options based on this text:"

# Make an API call to OpenAI to get job suggestions
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=50,  # Adjust the max_tokens as needed
    n = 1  # You can change the number of suggestions you want
)

# Extract the job suggestions from the response
suggested_jobs = response.choices[0].text.strip()

# Print the job suggestions
print("Suggested job options:")
print(suggested_jobs)

suggested_jobs_list = suggested_jobs.split('\n')

# Initialize a dictionary to store job options and their respective top 5 listings
job_listings = {}

# Loop through each suggested job option
for job_option in suggested_jobs_list:
    if not job_option:
        continue

    # Create a dictionary entry for the current job option
    job_listings[job_option] = []

    # Perform web scraping for the top 5 job listings for the current job option
    driver.get("https://www.naukri.com/")
    time.sleep(10)  # Adjust the sleep time as needed

    input_element = driver.find_element(By.XPATH, "//input[@placeholder='Enter skills / designations / companies']")
    input_element.send_keys(job_option)
    input_loc = driver.find_element(By.XPATH, "//input[@placeholder='Enter location']")
    input_loc.send_keys(loc)
    time.sleep(10)  # Adjust the sleep time as needed

    elementSearch = driver.find_element(By.CLASS_NAME, "qsbSubmit")
    elementSearch.click()
    time.sleep(10)  # Adjust the sleep time as needed

    job = driver.find_element(By.CLASS_NAME, "list")
    job_elements = job.find_elements(By.CLASS_NAME, "jobTuple")

    i = 0

    # Extract top 5 job listings for the current job option
    for job_ele in job_elements:
        if i >= 5:
            break

        job_title_element = job_ele.find_element(By.CLASS_NAME, "jobTupleHeader")
        job_info = job_title_element.find_element(By.CLASS_NAME, "info")
        job_company = job_info.find_element(By.CLASS_NAME, "companyInfo")
        job_element = job_company.find_element(By.CSS_SELECTOR, "a")

        job_listings[job_option].append(job_element.get_attribute('innerHTML'))
        i += 1

# Print the job options and their respective top 5 listings
for job_option, listings in job_listings.items():
    print(f"Job Option: {job_option}")
    for listing in listings:
        print(f"- {listing}")
