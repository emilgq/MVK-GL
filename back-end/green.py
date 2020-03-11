
import requests
import re
import pandas as pd
import json
from datetime import datetime
import dateutil.parser


# Stockholms kordinater på en höjd av 59
endpoint_url = "https://api.greenlytics.io/weather/v1/get_nwp"
headers = {"Authorization": ""}
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


#print
dategl = dateutil.parser.parse(df_green['valid_datetime'][1])
#dateygl = datetime.strptime((df_green['valid_datetime'][1]), "%Y-%m-%d %H:%M")
print(type(dategl))

# Adds column with as a datetime object where timezone is removed. Makes it possible to compare dataframes
df_green['date_valid_datetime'] = [(dateutil.parser.parse(row)).replace(tzinfo=None) for row in df_green['valid_datetime']]

# Adds column with date as a datetime object. Makes it possible to compare dataframes
df_load['date_Datetime'] = [(dateutil.parser.parse(rows)) for rows in df_load['Datetime']]

#print(df_green)
#print(df_load)

mergedSets = pd.merge(
    df_load,
    df_green,
    left_on=['date_Datetime'],
    right_on=['date_valid_datetime']
)

print(mergedSets)
#MAKES datetime from str to datetime, used to get weekday of%H:%M"
#datey = datetime.strptime((df_load['Datetime'][1]), "%Y-%m-%d%t%H:%M")
# print(datey)

#df["time_column_name"] = df["time_column_name"].apply(lambda x: datetime.datetime.strptime(x , "datetime_format"))


# print("Tempeture at heigt 59 is %s and CloudCoverage is %s" % (df['T_height_59'],df['CLCT']))
#print(type(df_load['Datetime'][1]))
for i in range(len(mergedSets)):
    print(mergedSets['date_Datetime'])
    # +1 för att få så att green och svks timmar stämmer överense
    #,df['V'][i]
    #psqlString(df['valid_datetime'][i])
    # DateTime uppdelad


    #psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df_green['T_height_59'][i],df_green['CLCT'][i],df_green['V_height_59'][i])

    #psqlString = datetime.strptime((df_load['Datetime'][1]), "%Y-%m-%d %H:%M")
    #print(psqlString)
    # Använd något i denna stil
    # --- psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s) " % (type(df_load['Datetime'][i]))

    #ANVÄND
    #psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df_load['Load'][i],df_load['Datetime'][i])
    #psqlString = "INSERT INTO greenlytics (date,time,T_height_,CLCT,Wind) values (%s, %s, %s, %s, %s) " % (str(dateAndTime[0]),str(dateAndTime[1]),df_green['T_height_59'][i],df_green['CLCT'][i],df_green['V_height_59'][i])
    #psqlString = "INSERT INTO greenlytics (datetime,T_height_,CLCT,Wind) values ( %s, %s, %s, %s) " % (df['valid_datetime'][i],df['T_height_59'][i],df['CLCT'][i],df['V_height_59'][i])
    # --- print(psqlString)
