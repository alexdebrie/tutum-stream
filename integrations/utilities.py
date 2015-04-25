import json
import os
import requests

ROOT_URL = "https://dashboard.tutum.co"
TOKEN = os.environ.get('TUTUM_TOKEN')
USERNAME = os.environ.get('TUTUM_USERNAME')
TUTUM_AUTH = os.environ.get('TUTUM_AUTH')

def get_resource(resource_uri):
    url = ROOT_URL + resource_uri
    headers = {"Accept": "application/json"}

    if TUTUM_AUTH:
        headers["Authorization"] = TUTUM_AUTH
    elif TOKEN and USERNAME:
        headers["Authorization"] =  "ApiKey {}:{}".format(USERNAME, TOKEN)

    r = requests.get(url, headers=headers)

    return r.text

