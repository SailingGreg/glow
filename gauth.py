#
#
#

# this just connects to glow api and pulls electricity usage
# and then generate a simple graph

# this file contains the auth module gauth(uname, upasswd)

import json
import time # for token expriy
from datetime import datetime
import requests
#from creds import *

#from terminalplot import plot
#from termplot import Plot
import plotext as plt

debug = True # used for debugging

api = "https://api.glowmarkt.com/api/v0-1/auth"
tokens = "https://api.glowmarkt.com/api/v0-1/auth/token"
#appid = "b0f1b774-a586-4f72-9edd-27ead8aa7a8d"


def gauth(appid, uname, upasswd):
    if debug: print(f"Credentials: {uname}, {upasswd}")

    # first we need an access token so need to call the auth interface
    # set headers and provide data
    headdata = { 'Content-Type' : "application/json",
                'applicationId': appid}
    payload = {"username": uname, "password": upasswd}

    # the auth call to get the token
    try:
        response = requests.post(api, headers = headdata, json = payload)
    except:
        print("Error occuried")
        exit(1)

    # copy access token and check expiry time
    response_json = response.json()
    accToken = response_json["token"]
    tokenExp = response_json["exp"]
    accountId = response_json["accountId"]
    local_time = time.ctime(tokenExp)
    if debug: print(f"Token expiry {tokenExp} - {local_time}")
    #print('Local time:', local_time)
    #print (json.dumps(response_json, sort_keys=True, indent=5))
    #print(response_json)

    return accToken

# end of file
