
import requests
import re
import pandas as pd
import json
from datetime import (datetime, date, timedelta)
import dateutil.parser

# Loads the data from yesterday at 01 hour to today at 01
# Use as Croonjob after 01
api_url = "http://35.228.239.24/api/v1/"
endpoint = "weather-data"
endpoint_url = api_url + endpoint

response = requests.get(endpoint_url)

df_weather = pd.read_json(response.text)

latest_retrievial_date = datetime.strptime("1901 01 01","%Y %m %d")
# Column 0 holds date len(df_weather)
# Gets the date from the newest data
for i in range(len(df_weather)):
    print(df_weather[0][i])
    date_list_str = re.search("([0-9]{2}\s[A-Z][a-z]{2}\s20[\d]{2})",df_weather[0][i])
    current_date = datetime.strptime(date_list_str[0],"%d %b %Y")
    print(current_date)
    if(current_date > latest_retrievial_date):
        latest_retrievial_date = current_date
print(latest_retrievial_date)



# Used to get the data starting from the latestretrived data

# Need to get the date from to days ago. GL API loads data from hour 00 and SVK from 01
# Loads SVK from the day before to get matching datetime with GL
load_Start_Date = latest_retrievial_date - timedelta(days=1)
today_Date = date.today()
# Yesterdays date string to send in API
load_Start_Str = load_Start_Date.strftime("%Y-%m-%d")
latest_date_Str = latest_retrievial_date.strftime("%Y-%m-%d")
today_Str = today_Date.strftime("%Y-%m-%d")



# Greenlytics API
# Weather for Stockholm coordinates. Returns Temperature, cloudcoverage and wind.
endpoint_url_GL = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": "1iqsmV9rE6UhCkyzosBpROkGVgv0BrQ87aCPqLtV4VrBPwf0HbSESt8twLuDj3lrKUmj9sSe"}
params = {
    'model': 'DWD_ICON-EU',
    'start_date': latest_date_Str + ' 00',
    'end_date': today_Str  + ' 03',
    'freqs': '24h',
    'coords': {'latitude': [59], 'longitude': [18], 'height': [59]},
    'variables': ['T', 'CLCT','V'],
    'as_dataframe': True
}
# greenlytics
response = requests.get(endpoint_url_GL, headers=headers, params={'query_params': json.dumps(params)})
df_green = pd.read_json(response.text)


# SVK API
# Energy Load i MKWh for Stockholm area.
date_start = load_Start_Str
date_end = today_Str
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



#print
#dategl = dateutil.parser.parse(df_green['valid_datetime'][1])
#dateygl = datetime.strptime((df_green['valid_datetime'][1]), "%Y-%m-%d %H:%M")

#Drop duplicates with same date in df_green
df_green_unique = df_green.drop_duplicates(["valid_datetime"])


# Adds column with as a datetime object where timezone is removed. Makes it possible to compare dataframes
df_green_unique['date_valid_datetime'] = [(dateutil.parser.parse(row)).replace(tzinfo=None) for row in df_green_unique['valid_datetime']]


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
