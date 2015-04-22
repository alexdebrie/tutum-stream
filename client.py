import os
import websocket
import json

from integrations.slack import post_slack
from integrations.pagerduty import pagerduty_event
 
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
        elif type != "user-notifications":
            print("{}:{}:{}:{}:{}".format(type, msg_as_JSON.get("action"), msg_as_JSON.get("state"), msg_as_JSON.get("resource_uri"), msg_as_JSON.get("parents")))
 
def on_open(ws):
    post_slack(text="Connected to Tutum Stream!")
    pagerduty_event(event_type='resolve', incident_key='tutum-stream', description='Tutum Stream connection open.')
    print "Connected"
 
if __name__ == "__main__":
    websocket.enableTrace(False)
    token = os.environ['TUTUM_TOKEN']
    username = os.environ['TUTUM_USERNAME']
 
    ws = websocket.WebSocketApp('wss://stream.tutum.co/v1/events?token={}&user={}'.format(token, username),
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open)
 
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        pass
