
import requests
import re
import math
import pandas as pd
import json
from datetime import (datetime, date, timedelta)
import dateutil.parser
from config import config


today_date = datetime.today()


# The date of 1 days ago. By calling the forecast from two days ago it's sure that is a forecas.
yesterday_Date = date.today() - timedelta(days=1)
# Yesterdays date string to send in API

yesterday_Str = yesterday_Date.strftime("%Y-%m-%d")

# string of start date of dataretriveal at hour 18
start_str = yesterday_Str + '  18'
# Makes Array with year , month , day
date_list = (yesterday_Str.split('-'))
#creates a datetime object that corresponds to the last retrieval,
# used to calculate the difference in hours between current hour and last retrieval
retrive_date_hour = datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]),18)

# difference in seconds since last retrieval
diff_dates = today_date-retrive_date_hour
# calculate the difference in hours to know what index to start from, rounded down
# Divide by 3600 seconds to get hours
diff_hours = math.floor(diff_dates.total_seconds()/3600)
print(diff_hours)

# Greenlytics API
# Weather forecast. Returns Temperature, cloudcoverage and wind.
endpoint_url = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": config()}
params = {
    'model': 'NCEP_GFS',
    'start_date': start_str ,
    'end_date': start_str ,
    'freqs': '6h',
    'coords': {'latitude': [59], 'longitude': [18], 'lv_HTGL2': [59.0], 'lv_ISBL7': [100000.0]},
    'variables': ['Temperature_Height', 'CloudCover_Isobar', 'WindGust'],
    'as_dataframe': True
}
response = requests.get(endpoint_url, headers=headers, params={'query_params': json.dumps(params)})
df_forecast = pd.read_json(response.text)

# Makes an extra column with Datetime object of valid_datetime to make it possible to change the form of the date
df_forecast['date_valid_datetime'] = [(dateutil.parser.parse(row)).replace(tzinfo=None) for row in df_forecast['valid_datetime']]


#Last forecast was retrived before the current days forecast
# Send data to forecast endpoint
# Casts cloudcover from num int64 to int so it's serializable in JSON
# 30 and 54 is the corrcet hours for todays index.
for i in range(diff_hours,(diff_hours+24)):
    # String of the timestamp with correct formation for the API
    date_Str = df_forecast['date_valid_datetime'][i].strftime("%Y-%m-%d %H:%M")
    endpoint_url = "http://35.228.239.24/api/v1/weather-forecast"
    headers = {"Content-Type" : "application/json"}
    params = {
    "timestamp": date_Str,
    "temperature": df_forecast['Temperature_Height_lv_HTGL2_59.0'][i],
    "cloud-cover": int(df_forecast['CloudCover_Isobar_lv_ISBL7_100000.0'][i]),
    "wind": df_forecast["WindGust"][i],
    "API-KEY": "MVK123"
    }
    response = requests.post(endpoint_url, headers=headers, data=json.dumps(params))
    print(response.text)
