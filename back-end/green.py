
import requests
import re
import pandas as pd
import json

# Stockholms kordinater på en höjd av 59 ger cloud coverage
endpoint_url = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": "1iqsmV9rE6UhCkyzosBpROkGVgv0BrQ87aCPqLtV4VrBPwf0HbSESt8twLuDj3lrKUmj9sSe"}
params = {
    'model': 'DWD_ICON-EU',
    'start_date': '2019-05-15 00',
    'end_date': '2019-05-16 00',
    'coords': {'latitude': [59], 'longitude': [18], 'height': [59]},
    'variables': ['T', 'CLCT','V'],
    'as_dataframe': True
}

#SVK
date_start = '2019-05-15'
date_end = '2019-05-16'
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
#df_load = df_load.drop(columns='Datetime')
df_load['Load'] = -df_load['Load']/10**3


# greenlytics
response = requests.get(endpoint_url, headers=headers, params={'query_params': json.dumps(params)})
df_green = pd.read_json(response.text)

#print(df)
# print("Tempeture at heigt 59 is %s and CloudCoverage is %s" % (df['T_height_59'],df['CLCT']))
for i in range(len(df_load['Load'])-1):
    # +1 för att få så att green och svks timmar stämmer överense
    dateAndTime = re.split(r"T",df_green['valid_datetime'][i+1])
    #,df['V'][i]
    #psqlString(df['valid_datetime'][i])
    # DateTime uppdelad

    #psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df_green['T_height_59'][i],df_green['CLCT'][i],df_green['V_height_59'][i])

    psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df_load['Load'][i],df_load['Datetime'][i])
    #psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df_green['T_height_59'][i],df_green['CLCT'][i],df_green['V_height_59'][i])
    #psqlString = "INSERT INTO greenlytics (datetime,T_height_,CLCT,Wind) values ( %s, %s, %s, %s) " % (df['valid_datetime'][i],df['T_height_59'][i],df['CLCT'][i],df['V_height_59'][i])
    print(psqlString)
