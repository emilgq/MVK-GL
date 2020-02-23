# Ger stockholms data
import pandas as pd
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

print(df_load)
for i in range(len(df_load['Load'])):
    psqlString = "INSERT INTO svk (date,time) values (%s, %s) " % (df_load['Load'][i],df_load['Datetime'][i],)
    print(psqlString)
