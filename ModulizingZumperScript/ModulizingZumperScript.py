

# This script usese BeautifulSoup to scrape the goals information of PL players for the tables that can be found on the offical Premier League Website. It demonstrates proficiencies in both Beautiful Soup and Pandas. 

# Import Libraries

from pathlib import Path
import selenium
import csv
import time
import urllib
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


listings_data = {
    'Listing Name':[],
    'Street Address':[],
    'City':[],
    'Postal Code':[],
    'Units':[],
    'Images':[],
    'About':[]
    }

# Open ChromeDrive
def openURL(url, list_start, list_end):

    host = '192.168.12.12'  # Define the Host and Port
    port = 12345

    driver = webdriver.Chrome(ChromeDriverManager().install())  # Define the Driver
    driver.get(url) # Get the PL Websitre

    driver.maximize_window()    # Maximize Window so the full screen information appears

    def listing_details():

        # Listing Name details
        listing_name = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/h1').text.split('\n')[0]
    
        # Scrape full address and append details accordingly
        address = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/h1/span').text
        address_list = address.split(", ")  # Split by comma to get details

        # Define the address details
        street_address = address_list[0]
        city = address_list[1]  
        postal_code = address_list[2].split(" ")[1] + " " + address_list[2].split(" ")[2]  # Postal code requires additional split to identify PC prefix

        about = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[3]/div').text

        listings_data['Listing Name'].append(listing_name)
        listings_data['Street Address'].append(street_address)
        listings_data['City'].append(city)
        listings_data['Postal Code'].append(postal_code)
        listings_data['About'].append(about)

    def grab_images():
    
        images = []    # Blank image list

        pic_section = '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[1]/div'   # Here is the xpath to picture section

        collage = driver.find_elements_by_xpath(pic_section)    # Identify the collage
        pc = len(collage)   # Get the number of photos in the collage

        for x in range(1, pc + 1):

            img_count = len(driver.find_elements_by_xpath(pic_section + '[' + str(x) + ']/div'))

            if img_count > 1:

                for y in range(1, img_count+1):

                    img = driver.find_element_by_xpath(pic_section + '[' + str(x) + ']/div[' + str(y) + ']/div/picture/img')
                    src = img.get_attribute('src')

                    images.append(src)

            else:

                img = driver.find_element_by_xpath(pic_section + '[' + str(x) + ']/div/div/picture/img')
                src = img.get_attribute('src')

                images.append(src)

        listings_data['Images'].append(images)

    def grab_fp():

        fp = {
            'Unit Type':[],
            'Specs':[],
            'Bathrooms':[],
            'Price':[],
            'SQFT':[]
            }

        try:    
            table_type = driver.find_element_by_class_name('Floorplans_headerText__3ejTe').text[:-1]

        except:
            table_type = 'Summary'

        if table_type == 'Summary':

            element = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[1]/div/div[2]')  # Here we define the view location the view for those w/o a floorplans section
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()  # This brings the floorplan section into view

            fp_name = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div[2]').text
            fp_bath = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div[2]').text
            fp_price = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/div/div[1]/div').text
            fp_sqft = driver.find_element_by_xpath('//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[3]/div[2]').text

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
                        fp_price = driver.find_element_by_xpath(fp_table + "div[" + str(j) + "]/div[2]/div[" + str(k) + "]/div/div[1]/div[2]/div[1]/div[2]").text

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
        name_xpath = '//*[@id="rail"]/div/div/div[1]/div[3]/div[1]/div[{listing}]/div/div/div[2]/div[1]/div[3]/a'.format(listing = i)

        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, name_xpath))).click()

        time.sleep(2)  # Time to rest prior to removing cookie pop up

        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div[4]/div/div[3]/div/button'))).click()

        listing_details()
        grab_images()
        grab_fp()

        time.sleep(1)  # Time to rest prior to removing cookie pop up

        driver.back()

   
openURL('https://www.zumper.com/apartments-for-rent/vancouver-bc', 3, 20)

listings_data

