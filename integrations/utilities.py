import json
import os
import requests

ROOT_URL = "https://dashboard.tutum.co"
TOKEN = os.environ['TUTUM_TOKEN']
USERNAME = os.environ['TUTUM_USERNAME']

def get_resource(resource_uri):
    url = ROOT_URL + resource_uri
    headers = {
        "Authorization": "ApiKey {}:{}".format(USERNAME, TOKEN),
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers)

    return r.text

