import os
import websocket
import json

from integrations.slack import generic_slack, post_slack
from integrations.pagerduty import pagerduty_event
from integrations.utilities import get_resource
 
def on_error(ws, error):
    print error
 
def on_close(ws):
    pagerduty_event(event_type='trigger', incident_key='tutum-stream', description='Tutum Stream connection closed.')
    print "### closed ###"
 
def on_message(ws, message):
    msg_as_JSON = json.loads(message)
    type = msg_as_JSON.get("type")
    if type:
        if type == "auth":
            print("Auth completed")
        elif type == "container":
            generic_slack(message)
        elif type == "service":
            parents = msg_as_JSON.get("parents")
            if parents:
                stack = get_resource(parents[0])
                stack_as_JSON = json.loads(stack)
                text = ("A Service on Tutum was {}d.\nIt belonged to the "
                        "{} Stack.\nThe Stack state is: {}".format(msg_as_JSON.get('action'),
                                                                  stack_as_JSON.get('name'),
                                                                  stack_as_JSON.get('state')))
                post_slack(text=text)
        elif type != "user-notifications":
            print("{}:{}:{}:{}:{}".format(type, msg_as_JSON.get("action"), msg_as_JSON.get("state"), msg_as_JSON.get("resource_uri"), msg_as_JSON.get("parents")))
 
def on_open(ws):
    pagerduty_event(event_type='resolve', incident_key='tutum-stream', description='Tutum Stream connection open.')
    print "Connected"
 
if __name__ == "__main__":
    websocket.enableTrace(False)
    token = os.environ.get('TUTUM_TOKEN')
    username = os.environ.get('TUTUM_USERNAME')
    TUTUM_AUTH = os.environ.get('TUTUM_AUTH')

    if TUTUM_AUTH:
        TUTUM_AUTH = TUTUM_AUTH.replace(' ', '%20')
        url = 'wss://stream.tutum.co/v1/events?auth={}'.format(TUTUM_AUTH)
    elif token and username:
        url = 'wss://stream.tutum.co/v1/events?token={}&user={}'.format(token, username)
    else:
        raise Exception("Please provide authentication credentials")

    ws = websocket.WebSocketApp(url, 
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = on_open)
 
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        pass
