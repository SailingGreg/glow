#
# file: gmtemps.py
#

# this just connects to glow api and pulls electricity usage
# and then generate a simple graph
# this checks if 'sensor' is available and if so
# download the temp for the last day

import json
import time # for token expriy
from datetime import datetime
import requests
from creds import *

from gauth import gauth
#from terminalplot import plot
#from termplot import Plot
import pandas as pd
import plotext as plt

debug = True # used for debugging

#api = "https://api.glowmarkt.com/api/v0-1/auth"
tokens = "https://api.glowmarkt.com/api/v0-1/auth/token"
veIds = "https://api.glowmarkt.com/api/v0-1/virtualentity"
veIdsv2 = "https://api.glowmarkt.com/api/v0-1/virtualentity/{veId}/resources"
veResource = "https://api.glowmarkt.com/api/v0-1/resources"
resIdv2 = "https://api.glowmarkt.com/api/v0-1/resource/{resId}/readings?"
resIdTypev2 = "https://api.glowmarkt.com/api/v0-1/resourcetype/{typeId}"
appid = "b0f1b774-a586-4f72-9edd-27ead8aa7a8d"


#
# functions
#
def getveIds(accToken, appid):
    # we now have an access token and can elaborate the data - veId/resources
    headdata = { 'Content-Type' : "application/json",
            'applicationId': appid,
            'token': accToken}
            #'accountId': accountId,


    # we now list the elements of the system
    response = requests.get(veIds, headers = headdata)
    #print(response )
    response_veids = response.json()
    #print(response_veids)

    # format and print
    #print (json.dumps(response_veids, sort_keys=True, indent=5))
    #print (response_veids["resources"])

    return (response_veids)
# end getveIds()


# there can be multiple entries if we have a sensor
def extractResId(response_veids, resStr):
    tempResId = None
    #print (response_veids)
    for slice in response_veids:
        print ("Name: ", slice["name"], " Id: ", slice["veId"])
        #for key in slice:
        #if (slice["name"] == "DCC Sourced"):
        #if (slice["name"] == "Multisensor 040d8428212e"):

        # we should be able to flaten this is resource name is unique
        if ("Multisensor" in slice["name"]):
            # note the resourcId is included!
            for res in slice["resources"]:
                print (res["name"], res["resourceId"])

                # do we have the 'temperature'
                #if ("Temperature" in res["name"]):
                if (resStr in res["name"]):
                    tempResId = res["resourceId"]

            veId = slice["veId"] # note the virtial endpoint id

    print(f"veId is {veId}")
    print(f"tempResId is {tempResId}")

    return tempResId
# end extractResId()

# build the params for the query
def queryRange(qtype):
    now = datetime.now() # time.ctime()
    # this is just the end of today
    dayFinish = f"{now.year}-{now.month:02d}-{now.day:02d}T23:59:59"

    if (qtype == 'today'):
        dayStart = f"{now.year}-{now.month:02d}-{now.day:02d}T00:00:00"
    elif (qtype == 'day'):
        # for the last 24 hours - this changes the 'start'
        tim = time.time() # 
        tim = tim - (24 * 60 * 60) # minus 1 day
        dday = datetime.fromtimestamp(tim) # date object
        dayStart = f"{dday.year}-{dday.month:02d}-{dday.day:02d}T{dday.hour:02d}:{dday.minute:02d}:00"
    elif (qtype == 'week'):
        tim = time.time() # 
        tim = tim - (7 * 24 * 60 * 60) # minus 1 week
        dday = datetime.fromtimestamp(tim) # date object
        dayStart = f"{dday.year}-{dday.month:02d}-{dday.day:02d}T{dday.hour:02d}:{dday.minute:02d}:00"
        #print(dday.hour, dday.minute, last24)
#lastday = 

    return dayStart, dayFinish
# end queryRange()

def getResReadings(resId, dayStart, dayFinish, headdata):
    #'period': 'P1W',
    #'period': 'PT30M',
    #'period': 'PT1H', # doesn't work for temps!
    #'period': 'PT1D', # doesn't work for temps!
    #'period': 'PT1W', # doesn't work for temps!
    paramQuery = { 'from' : dayStart,
            'to': dayFinish,
            'period': 'PT30M',
            'function': 'avg',
            'offset': 0}

    # constructure the url based on resourseId
    myresId = eval(f"f'{resIdv2}'")
    #print (myresId)
    #print(myresId)

    try:
        response = requests.get(myresId, headers=headdata, params=paramQuery)
    except:
        print (f"Error on {resId}" )
    #print (response)
    response_resId = response.json()

    #print (json.dumps(response_resId, sort_keys=True, indent=4))
    #print (response_resId["units"], response_resId["data"])
    print (response_resId["units"])
    return(response_resId)
# end getResReadings()

#
# the main flow
#

# get the access token based on the app and user credentials
accToken = gauth(appid, uname, upasswd)
# get the veId structure
veIdStruct = getveIds(accToken, appid)

# find the resource with the veIds
resName = "Temperature"
tempResId = extractResId(veIdStruct, resName)

if (tempResId is None):
    print(f"Didn't find the {resName} resId")
    exit (1)
print (f"ResId for {resName}, {tempResId}")

# need this for the calls below
headdata = { 'Content-Type' : "application/json",
            'applicationId': appid,
            'token': accToken}

# define the start/finish range - today, day, week, month
queryType = 'today'
dayStart, dayFinish = queryRange(queryType) 
queryType = 'day'
dayStart, dayFinish = queryRange(queryType) # 24hours
queryType = 'week'
dayStart, dayFinish = queryRange(queryType) # 24hours
print (dayStart, dayFinish)
#dayStart, dayFinish = queryRange('week') # 1 week

print (f"Query range is {dayStart}, {dayFinish}")

# now extract the data
response_resId = getResReadings(tempResId, dayStart, dayFinish, headdata)

# and now plot and display

# need to chagne offset for BST - offset = -60
# appears offset is ignored and start/finish are taken to be localtime
# so during bst hours are offset (reduced) by 1

# we can now pull the readings for the specific service - cost & consump

# load the time/value into a dataframe for manipluation
# this has structure of int64, float64
df = pd.DataFrame(response_resId["data"])
# add labels for convience
df.columns = ["date","temp"]
#print(df.head())

'''
# check first entry's date
stime = df['date'][0]
local_time = time.ctime(stime) # this deals with tz
print(f"{df['date'][0]} -> {local_time}")
'''

# and convert time() to date type - unit is seconds
#df['date'] = pd.to_datetime(df['date'], unit ='s', tz=True)
df['date'] = pd.to_datetime(df['date'], unit ='s')
# following adds an hour if BST!
#df.date = df.date + pd.Timedelta('01:00:00')
print(df.info())
print(df.head())
print(df.tail())
#print(df)

'''
# for this we need to datetimeindex
df2 = df.set_index(pd.DatetimeIndex(df['date']))
print(df2)
df3 = df2.resample('10min')
print (df3.head())
'''

# now aggregate based on minutes to reduce data points
#print ("Grouping")
# options are sum/mean
if (queryType == 'today' or queryType == 'day'):
    grouped = df.groupby(pd.Grouper(key='date', axis=0, freq='10min')).mean()
else:
    grouped = df.groupby(pd.Grouper(key='date', axis=0, freq='30min')).mean()

print(grouped.info())
#print(grouped)

# we can now plot the dateframe
plt.clf()
# we need to define the structure of the date
plt.date_form('Y-m-d H:M:S')
# note the first column is the index
dates = plt.datetimes_to_string(grouped.index)
temps = list(grouped["temp"])


now = datetime.now() # time.ctime()
#plt.scatter(grouped['temp']) # y
plt.plot(dates, temps) # y
if (queryType == 'today'):
    hdrStr = "Today's"
elif (queryType == 'day'):
    hdrStr = "24 hour"
else:
    hdrStr = "Weekly"
plt.title(f"{hdrStr} temperature {now.day:02d}-{now.month:02d}-{now.year}")
plt.show()

# end of file
