from pathlib import Path
import urllib
import pandas as pd
from pandas.io.pytables import IndexCol
from ast import literal_eval
from datetime import date

def images_file(file_name):

    # Define the blank image dataframe
    image_df = pd.DataFrame(columns=['Listing ID','Listing Name','Image URL'])

    listings_df = pd.read_excel(r'C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/Master/{name}.xlsx'.format(name = file_name), index_col=0)

    images = listings_df[['Listing Name','Images']]

    for i in range(0, len(images)):

        # Identify the floorplans list within the listing df
        u_index  = (images.index[i])
        listing_name = images.loc[i+1000, 'Listing Name']
        images.loc[i+1000, 'Images'] = literal_eval(images.loc[i+1000, 'Images'])

        for j in range(0, len(images.loc[i+1000, 'Images'])):

            image = images.loc[i+1000, 'Images'][j]

            image_df = image_df.append({'Listing ID':u_index, 'Listing Name':listing_name, 'Image URL':image}, ignore_index=True)

    image_df.index += 90000

    image_df.to_csv('C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/Master/Images_{location}'.format(location = 'master_') + str(date.today()) + '.csv', index=True)

images_file('master_2022-04-25')








