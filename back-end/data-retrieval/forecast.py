
import requests
import re
import pandas as pd
import json
from datetime import (datetime, date, timedelta)
import dateutil.parser


# The date of two days ago. By calling the forecast from two days ago it's sure that is a forecas.
yesterday_Date = date.today() - timedelta(days=2)
# Yesterdays date string to send in API
yesterday_Str = yesterday_Date.strftime("%Y-%m-%d") + "  18"

# Greenlytics API 2
# Weather forecast. Returns Temperature, cloudcoverage and wind.
endpoint_url = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": "1iqsmV9rE6UhCkyzosBpROkGVgv0BrQ87aCPqLtV4VrBPwf0HbSESt8twLuDj3lrKUmj9sSe"}
params = {
    'model': 'NCEP_GFS',
    'start_date': yesterday_Str,
    'end_date': yesterday_Str,
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
for i in range(30,54):
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
