from pathlib import Path
import urllib
import pandas as pd
from pandas.io.pytables import IndexCol
from ast import literal_eval
from datetime import date

def units_file(file_name):

    # Define the blank image dataframe
    fp_df = pd.DataFrame(columns=['Listing ID','Unit Type','Specs','Bathrooms','Price','SQFT'])

    listings_df = pd.read_excel(r'C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/Master/{name}.xlsx'.format(name = file_name), index_col=0)

    # Isolate the units lists
    units_df = listings_df['Units']

    for i in range(0, len(units_df)):

        # Identify the floorplans list within the listing df
        u_index  = (units_df.index[i])
        units_data = literal_eval(units_df.iloc[i])

        for j in range(0, len(units_data['Unit Type'])):

            # Identify the column informaton and its location
            unit = units_data['Unit Type'][j]
            specs = units_data['Specs'][j]
            bath = units_data['Bathrooms'][j]
            price = units_data['Price'][j]
            size = units_data['SQFT'][j]

            # Append to the data frame
            fp_df = fp_df.append({'Listing ID':u_index, 'Unit Type':unit, 'Specs':specs, 'Bathrooms':bath, 'Price':price, 'SQFT':size}, ignore_index=True)

    # Set the index at 10000
    fp_df.index += 10000

    # Print and convert to excel
    print(fp_df.to_string())
    fp_df.to_csv('C:/Users/robert.enright/Downloads/SwitchAppartmentData/Extracts/Master/Units_{location}'.format(location = 'master_') + str(date.today()) + '.csv', index=True)

units_file()