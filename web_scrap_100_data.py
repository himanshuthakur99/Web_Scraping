from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from pymongo import MongoClient

def fetch_profiles_from_html(html):
    profiles = []
    soup = BeautifulSoup(html, 'html.parser')
    
    profile_cards = soup.find_all('div', class_='list-product-description product-description-brd')
    
    for card in profile_cards:
        profile = {}
        
        # Extract Expert ID
        try:
            expert_id_tag = card.find('ul', class_='list-inline add-to-wishlist pull-right').find('li')
            if expert_id_tag:
                expert_id = expert_id_tag.text.strip().split(':')[-1].strip()
                profile['Expert ID'] = expert_id
            else:
                profile['Expert ID'] = 'N/A'
        except AttributeError:
            profile['Expert ID'] = 'N/A'
        
        # Extract Name
        try:
            profile['Name'] = card.find('h4', class_='title-price').find('strong').text.strip()
        except AttributeError:
            profile['Name'] = 'N/A'
        
        # Extract Designation
        try:
            profile['Designation'] = card.find('span', class_='title-price').text.strip()
        except AttributeError:
            profile['Designation'] = 'N/A'
        
        # Extract Expertise
        try:
            expertise = card.find('ul', class_='list-inline margin-bottom-5').find('i', class_='flaticon-light96').find_next('b').text.strip()
            profile['Expertise'] = expertise
        except AttributeError:
            profile['Expertise'] = 'N/A'
        
        # Extract Institution
        try:
            institution = card.find_all('ul', class_='list-inline add-to-wishlist')[-1].find_all('li')[0].text.strip()
            profile['Institution'] = institution
        except (AttributeError, IndexError):
            profile['Institution'] = 'N/A'
        
        # Extract Location
        try:
            location = card.find_all('ul', class_='list-inline add-to-wishlist')[-1].find_all('li')[1].text.strip()
            profile['Location'] = location
        except (AttributeError, IndexError):
            profile['Location'] = 'N/A'
        
        profiles.append(profile)
    
    return profiles

def scrape_profiles(driver, url):
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    all_profiles = []
    
    # Loop through the first 10 pages
    for page in range(1, 11):
        html = driver.page_source
        profiles = fetch_profiles_from_html(html)
        all_profiles.extend(profiles)
        
        # Click the next button to go to the next page
        try:
            next_button = driver.find_element(By.LINK_TEXT, str(page+1))
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
        except Exception as e:
            print(f"Exception occurred: {e}")
            print("No more pages or next button not found.")
            break
    
    return all_profiles

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

def save_to_mongodb(data, collection_name):
    client = MongoClient('localhost', 27017)
    db = client['vidwan_profiles']
    collection = db[collection_name]
    collection.insert_many(data)
    print(f"Data saved to MongoDB collection '{collection_name}'")

if __name__ == '__main__':
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    vidwan_url = 'https://vidwan.inflibnet.ac.in/searchc/search'
    
    # Scrape profiles
    profiles_data = scrape_profiles(driver, vidwan_url)
    
    # Save to Excel
    excel_filename = f"vidwan_profiles_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    save_to_excel(profiles_data, excel_filename)
    
    # Save to MongoDB
    collection_name = f"vidwan_profiles_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    save_to_mongodb(profiles_data, collection_name)
    
    driver.quit()
# # Schedule the task to run every 15 days
# schedule.every(15).days.do(main)

# if getting any error run this commands
# -----------------------------------------
# pip install selenium webdriver_manager pandas

# pip install requests beautifulsoup4 pandas openpyxl pymongo schedule
# python --version
# python -m pip install --upgrade pip
# pip uninstall numpy
# pip uninstall scipy
