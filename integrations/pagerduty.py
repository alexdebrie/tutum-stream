import json
import os
import requests

PAGERDUTY_URL = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'
PAGERDUTY_KEY = os.environ.get('PAGERDUTY_KEY', '')

def pagerduty_event(event_type="trigger", incident_key=None, description=None, client=None, client_url=None, service_key=PAGERDUTY_KEY):
    if not service_key:
       raise Exception("Please provide a Pagerduty Service Key")

    if not description:
        description = "Tutum Stream Issue"
    
    data = {
        "service_key": service_key,
        "incident_key": incident_key,
        "event_type": event_type,
        "description": description,
        "client": client,
        "client_url": client_url
    }
            
    headers = {'Content-type': 'application/json'}
    r = requests.post(PAGERDUTY_URL,
                     headers=headers,
                     data=json.dumps(data))
    
    if r.status_code == 200:
        print "Posted {} to Pagerduty.".format(event_type)
    else:
        print "Failed to post {} to Pagerduty.".format(event_type)
        error_code = r.json().get('error').get('code')
        message = r.json().get('error').get('message')
        errors = r.json().get('error').get('errors')
        print "{} ({}): {}".format(message, error_code, errors)
