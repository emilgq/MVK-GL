
import requests
import re
import pandas as pd
import json
from datetime import datetime
import dateutil.parser
from config import config

# Greenlytics API
# Weather for Stockholm coordinates. Returns Temperature, cloudcoverage and wind.
endpoint_url = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": config()}
params = {
    'model': 'DWD_ICON-EU',
    'start_date': '2020-03-20  00',
    'end_date': '2020-03-21 00',
    'coords': {'latitude': [59], 'longitude': [18], 'height': [59]},
    'variables': ['T', 'CLCT','V'],
    'as_dataframe': True
}
# greenlytics
response = requests.get(endpoint_url, headers=headers, params={'query_params': json.dumps(params)})
df_green = pd.read_json(response.text)


# SVK API
# Energy Load i MKWh for Stockholm area.
date_start = '2020-03-20'
date_end = '2020-03-21'
area = 'STH'
url_base = 'https://mimer.svk.se/'
url_target = 'ConsumptionProfile/DownloadText?groupByType=0&' + \
             'periodFrom='+date_start+'&' + \
             'periodTo='+date_end+'&' + \
             'networkAreaIdString='+area
url = url_base+url_target
df_load = pd.read_csv(url, sep=';', header=1, decimal=',', usecols=[0,1], names=['Datetime', 'Load'])
df_load = df_load[:-1]
df_load.index = pd.to_datetime(df_load['Datetime'])
df_load['Load'] = -df_load['Load']/10**3


# Makes datetime object of date in a new column, timezone removed.
# Used when merging GL dataframe and Load dataframe
df_green.loc[:,'date_valid_datetime'] = [(dateutil.parser.parse(row)).replace(tzinfo=None) for row in df_green['valid_datetime']]

#Drop duplicates with same date in df_green and makes it a view
df_green_unique = df_green.drop_duplicates(["valid_datetime"])

# Adds column with date as a datetime object. Makes it possible to compare dataframes
df_load['date_Datetime'] = [(dateutil.parser.parse(rows)) for rows in df_load['Datetime']]


# Merges on the datetime type where they're equal. Keeps both of the columns.
mergedSets = pd.merge(
    df_load,
    df_green_unique,
    left_on=['date_Datetime'],
    right_on=['date_valid_datetime']
)

mergedSets.dropna()

# Posts the merged dataframe to rest-API
for i in range(len(mergedSets)):
    endpoint_url = "http://35.228.239.24/api/v1/weather-data"
    headers = {"Content-Type" : "application/json"}
    params = {
    "timestamp": mergedSets["Datetime"][i],
    "temperature": mergedSets["T_height_59"][i],
    "cloud-cover": mergedSets["CLCT"][i],
    "wind": mergedSets["V_height_59"][i],
    "consumption": mergedSets["Load"][i],
    "API-KEY": "MVK123"
    }
    response = requests.post(endpoint_url, headers=headers, data=json.dumps(params))
    print(response.text)
