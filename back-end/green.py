
import requests
import re
import pandas as pd
import json

# Stockholms kordinater på en höjd av 59 ger cloud coverage
endpoint_url = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": ""}
params = {
    'model': 'DWD_ICON-EU',
    'start_date': '2019-05-15 00',
    'end_date': '2019-05-15 10',
    'coords': {'latitude': [59], 'longitude': [18], 'height': [59]},
    'variables': ['T', 'CLCT','V'],
    'as_dataframe': True
}
response = requests.get(endpoint_url, headers=headers, params={'query_params': json.dumps(params)})
df = pd.read_json(response.text)

#print(df)
# print("Tempeture at heigt 59 is %s and CloudCoverage is %s" % (df['T_height_59'],df['CLCT']))
for i in range(len(df['T_height_59'])):
    dateAndTime = re.split(r"T",df['valid_datetime'][i])
    #,df['V'][i]
    psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df['T_height_59'][i],df['CLCT'][i],df['V_height_59'][i])
    print(psqlString)
    #print(df['valid_datetime'][i])
