# Zones taken from http://www.bgpost.bg/bg/347
# BG Posts apply a 1.50 euro tax for orders above 2kg!
import os, math
import pandas as pd

xls = pd.ExcelFile("../zones.xls")

# Parse sheet number,
# "df" is short for "dataframe"
df = xls.parse(0)

# Remove unneeded columns
df = df.drop('Unnamed: 13', axis=1)

# Rename columns, "DTS" meaning: http://www.bgpost.bg/bg/506
headers = ['number', 'code', 'country_bg', 'country_en',
           'land_zone', 'land_max_weight_kg', 'land_max_value_dts', 'land_category',
           'air_zone', 'air_max_weight_kg', 'air_max_value_dts', 'air_category',
           'letters_max_value_dts']

df.columns = headers

# Remove first row containing old column names
df = df.iloc[1:]

# Create new columns
df['shipping_method'] = ''
df['zone'] = ''

def addShippingMethod(row):
    if (type(row['land_zone']) is not str) and (type(row['air_zone']) is not str):
        if not math.isnan(row['land_zone']) and not math.isnan(row['air_zone']):
            row['shipping_method'] = 'mixed'
            row['zone'] = 'mixed'

    elif type(row['land_zone']) is str:
        row['shipping_method'] = 'air'
        row['zone'] = row['air_zone']

    else:
        row['shipping_method'] = 'land'
        row['zone'] = row['land_zone']

    return row

# Fill the new columns
df.apply(addShippingMethod, axis=1)

# Remove rows in column 'code' containing spaces using regex
pattern = r'(^.*\s.*$)'
df = df[df['code'].str.contains(pattern) == False]

# Remove Somalia ¯\_(ツ)_/¯ щото БГ пощи не пращат до там
df = df[df['code'] != 'SO']

pd.set_option('display.width', 1080)
with pd.option_context('display.max_rows', None, 'display.max_columns', 7):
    # Check to see if new columns are correct
    print(df[['code', 'country_en', 'zone', 'shipping_method',  'land_zone', 'air_zone']])

for name in ['land', 'air', 'mixed']:
    dataframe = df[df['shipping_method'] == name]

    if name == 'mixed':
        dataframe = dataframe[['code', 'land_zone', 'air_zone', 'country_en']]
        dataframe = dataframe.sort_values('country_en')
        dataframe = dataframe.set_index('code')
    else:
        dataframe = dataframe[['code', 'shipping_method', 'zone', 'country_en']]
        dataframe = dataframe.sort_values('zone')
        dataframe = dataframe.set_index('zone')

    file_path = os.path.dirname(os.path.realpath(__file__)) + '/../{}_zones.csv'.format(name)
    dataframe.to_csv(file_path)
