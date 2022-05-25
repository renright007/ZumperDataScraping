

# This script usese BeautifulSoup to scrape the goals information of PL players for the tables that can be found on the offical Premier League Website. It demonstrates proficiencies in both Beautiful Soup and Pandas. 

# Import Libraries

import datetime
from pathlib import Path
import selenium
import csv
import time
import signal 
import urllib
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


# Open ChromeDrive
def openURL(url, list_start, list_end, append):

    listings_data = {
    'Listing Name':[],
    'Listing URL':[],
    'Managed By':[],
    'Street Address':[],
    'City':[],
    'Postal Code':[],
    'Units':[],
    'Images':[],
    'About':[]
    }

    host = '192.168.12.12'  # Define the Host and Port
    port = 12345

    driver = webdriver.Chrome(ChromeDriverManager().install())  # Define the Driver
    driver.get(url) # Get the PL Websitre
    driver.maximize_window()    # Maximize Window so the full screen information appears

    def listing_details():

        # Grab the listing URL
        listing_url = driver.current_url

        # Listing Name details
        listing_name = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/h1'))).text.split('\n')[0]

        # Get the management details
        managed_by_str = driver.find_element_by_xpath('//div[@data-testid="details"]').text.split('\n')[0]

        if 'Managed by' in managed_by_str:
            managed_by = managed_by_str
        else:
            managed_by = 'Not listed'

        # Scrape full address and append details accordingly
        address = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/h1/span').text
        address_list = address.split(", ")  # Split by comma to get details

        # Define the address details
        street_address = address_list[0]
        city = address_list[1]  
        postal_code = address_list[2].split(" ")[1] + " " + address_list[2].split(" ")[2]  # Postal code requires additional split to identify PC prefix

        try:
            about = driver.find_element_by_class_name('css-1puvci5').text
        except:
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[1]/div')))
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            about = 'No information.'

        listings_data['Listing Name'].append(listing_name)
        listings_data['Listing URL'].append(listing_url)
        listings_data['Managed By'].append(managed_by)
        listings_data['Street Address'].append(street_address)
        listings_data['City'].append(city)
        listings_data['Postal Code'].append(postal_code)
        listings_data['About'].append(about)

    def grab_images():
    
        image_list = []    # Blank image list
    
        images = driver.find_elements_by_tag_name('img')    # Find all image elements

        for image in images:    # Now we must locate the actual listing photos

            listing_prefix  = 'https://img.zumpercdn.com'   # We know that they have this prefix
            image_url = image.get_attribute('src')          # Get the image URL
        
            dim_suffix = '1280x960?fit=crop&h=900&w=1000'   # Define the format of the desired dimensions.

            if image_url is None:       # Ignore those that return None
                pass

            elif listing_prefix in image_url:
            
                # Split out the string and replace the existing suffice with our desired one
                scaled_url = image_url.split('/')
                scaled_url[-1] = dim_suffix

                # Join the ammended list as a string and append to our list
                scaled_url = '/'.join(scaled_url)
                image_list.append(scaled_url)

        listings_data['Images'].append(image_list)

    def grab_fp():

        fp = {
            'Unit Type':[],
            'Specs':[],
            'Bathrooms':[],
            'Price':[],
            'SQFT':[]
            }

        try:    
            #table_type = driver.find_element_by_class_name('Floorplans_headerText__3ejTe').text[:-1]
            table_type = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'Floorplans_headerText__3ejTe'))).text[:-1]

        except:
            table_type = 'Summary'

        if table_type == 'Summary':

            # Insert code to distinguish between those with 

            element = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[1]/div/div[2]')  # Here we define the view location the view for those w/o a floorplans section
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()  # This brings the floorplan section into view

            try:
                fp_name = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]').text
                fp_bath = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div[2]').text
                fp_price = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/div/div[1]/div').text[1:]
                fp_sqft = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[3]/div[2]').text

            except:
                fp_name = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[3]/div[1]/div[2]').text
                fp_bath = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[3]/div[2]/div[2]').text
                fp_price = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/div/div[1]/div').text[1:]
                fp_sqft = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[3]/div[3]/div[2]').text

            if fp_sqft in ['-','Dogs & Cats OK']:
                fp_sqft = 'Not Listed'

            else:
                fp_sqft = fp_sqft.split(' ')[0]

            fp['Unit Type'].append(fp_name)
            fp['Specs'].append(fp_name)
            fp['Bathrooms'].append(fp_bath)
            fp['Price'].append(fp_price)
            fp['SQFT'].append(fp_sqft)

        else:

            floorplans = driver.find_elements_by_class_name("css-o6i9hf")   # Using the class name, we can get a list of the floorplans
            fpc = len(floorplans)   # Count the amount that exist within the listing

            fp_table = "//*[@id='root']/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[1]/div/" # Define the xpath to the floorplan section
            
            for j in range(1, fpc + 1):

                fp_click = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[1]/div[2]/div[1]/div[1]")
                fp_click.click()    # Click floorplan to expand details

                unit_type = fp_click.text[:-1]   # Grab floorplan type

                unit_plans = int(driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[1]/div[2]/div[2]").text.split(' ')[0]) # Isolate the integer value for the number of floor plans

                if unit_plans > 1:  # If there are more than one, we must use a loop to scrape all unit plans

                    for k in range(1, unit_plans+1):    # For loop to grab all unit info within the floorplan
                
                        # Define values for the floorplan information, using j within the floorplan section and k within the unit plans
                        fp_name = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div[" + str(k) + "]/div/div[1]/div[2]/div[1]/div[1]").text     
                        fp_bath = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div[" + str(k) + "]/div/div[1]/div[2]/div[2]").text
                        fp_sqft = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div[" + str(k) + "]/div/div[1]/div[2]/div[3]/span").text
                        fp_price = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div[" + str(k) + "]/div/div[1]/div[2]/div[1]/div[2]").text[1:]

                        if fp_sqft in ['-','Dogs & Cats OK']:
                            fp_sqft = 'Not Listed'

                        else:
                            fp_sqft = fp_sqft.split(' ')[0]

                        fp['Unit Type'].append(unit_type)
                        fp['Specs'].append(fp_name)
                        fp['Bathrooms'].append(fp_bath)
                        fp['Price'].append(fp_price)
                        fp['SQFT'].append(fp_sqft)

                else:

                    fp_name = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]").text
                    fp_bath = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div/div/div[1]/div[2]/div[2]/span").text
                    fp_sqft = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div/div/div[1]/div[2]/div[3]/span").text
                    fp_price = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div/div/div[1]/div[2]/div[1]/div[2]").text[1:]

                    # We must format the SQFT field to avoid errors when converting to CSV
                    if fp_sqft in ['-','Dogs & Cats OK']:
                        fp_sqft = 'Not Listed'

                    else:
                        fp_sqft = fp_sqft.split(' ')[0]

                    fp['Unit Type'].append(unit_type)
                    fp['Specs'].append(fp_name)
                    fp['Bathrooms'].append(fp_bath)
                    fp['Price'].append(fp_price)
                    fp['SQFT'].append(fp_sqft)

                        
        listings_data['Units'].append(fp)
      
    listings_table = '//*[@id="rail"]/div/div/div[1]/div[3]/div[1]'
    r = driver.find_elements_by_xpath(listings_table + "/div")    # Get the row lenght
    rc = len (r)

    for i in range(list_start, list_end):

        # Click first photo to enter full screen mode
        name_xpath = '//*[@id="rail"]/div/div/div[1]/div[3]/div[1]/div[{listing}]/div/div/div[1]/img'.format(listing = i)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, name_xpath))).click()
        except:
            break

        about_xpaths = ['//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[3]/div/button',
                        '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[3]/div[1]/button',
                        '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[2]/div[1]/button',
                        '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[2]/div/button'
                        '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[2]/div[1]/button']
        
        for link in about_xpaths:

            try:
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, link))).click()
            except:
                pass

        try:
            listing_details()
            grab_images()
            grab_fp()
        except:
            continue

        driver.back() 

    driver.quit()

    location_str = url.split('/')[-1].replace('?page=', '-page-')

    listings_df = pd.DataFrame.from_dict(listings_data)    # Convert to data frame
    listings_df.index += 1000   # Start the index at 1000
    listings_df['Created Date'] = date.today()

    if append is 'N':

        listings_df.index += 1000   # Start the index at 1000
        listings_df.to_csv('C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/{location}-'.format(location = location_str) + str(date.today()) + '.csv', index=True)
        listings_df.to_excel('C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/{location}-'.format(location = location_str) + str(date.today()) + '.xlsx', index=True)

    elif append is 'Y':

        master_df = pd.read_csv(r'C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/Master/Master.csv', index_col=0)
        
        try:
            master_df.append(listings_df)
        except:
            print('Error, append failed')

    else:
        print('Invalid selection - choose either Y or N')

openURL('https://www.zumper.com/rentals/vancouver-bc/west-end', 1, 16, 'N')


