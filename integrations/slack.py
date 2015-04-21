import json
import os
import requests

SLACK_URL = os.environ.get('SLACK_URL', '')

def post_slack(text=None, slack_url=SLACK_URL):
    if not SLACK_URL:  
        raise Exception('Please provide a Slack URL')
    if not text:
        text = "You received a message from Tutum Stream!"
    data = {"text": text}
    r = requests.post(slack_url, data=json.dumps(data))
    return r
    
def generic_slack(message):
    msg_as_JSON = json.loads(message)
    text = ("Your {} was {}d on Tutum!\n" 
            "Check {} to see more details.".format(msg_as_JSON.get('type'),
                                                   msg_as_JSON.get('action'),
                                                   msg_as_JSON.get('resource_uri')))
    post_slack(text=text)
    
