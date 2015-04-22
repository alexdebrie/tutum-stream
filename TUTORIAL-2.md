#Using the new Tutum Stream API
## Part Two: Practical Use Cases of the Tutum Stream API

##Introduction

Tutum recently introduced its new [Tutum Stream API](http://blog.tutum.co/2015/04/07/presenting-tutum-stream-api/).
This is a great new feature that allows you to use WebSockets to monitor
Events from your Tutum account. WebSockets are a big improvement over
long-polling and other conventional HTTP-based methods to stay informed
of changes to your application.

This is part two of a two-part tutorial will show you how to use the
Tutum Stream API. This part will show how to use the Tutum Stream
API for some common use cases, such as integrations with Slack, Pagerduty,
and others. It shows how you can retrieve additional information from the
Tutum API to provide richer detail to your monitoring tools.
Finally, we'll see how to deploy a service on Tutum that is always
connected to the Tutum Stream API to keep you apprised of changes to your
deployments.

To follow along with this tutorial, clone [this GitHub repo](https://github.com/alexdebrie/tutum-stream).
It has a few sample client files as well as Python modules with code to
interact with Pagerduty, Slack, and Tutum. It also has a Dockerfile that you can use to
build a Docker image to deploy as a service on Tutum.

##The Four WebSocket Events

As noted in the previous tutorial, there are four event handlers you need to set
up with your WebSocket connection. These event handlers are:

    on_open: for when the connection to the WebSocket is opened;
    on_close: for when the connection to the WebSocket is closed;
    on_message: for when your WebSocket client receives a message;
    on_error: for when you receive an error

These four handlers will be the key to interacting with the Tutum Stream API.

##First Steps with the Tutum Stream Client

To get started with the Tutum Stream API, let's just run the basic example client
that Tutum showed in its [initial blog post]((http://blog.tutum.co/2015/04/07/presenting-tutum-stream-api/)
on the Tutum Stream API. If you cloned my GitHub repo, it is listed as
`tutum-sample.py`. You'll need to set two environment variables in your terminal
before running it.

    export TUTUM_TOKEN=<your_Tutum_token>
    export TUTUM_USERNAME=<your_Tutum_username>

These will be used to authenticate your WebSocket client with the Tutum Stream
server. Once you've set these, run:

    python tutum-sample.py

You should see the following output in your terminal:

    Connected
    Auth completed

If you look at the source code for `tutum-sample.py`, you see that that
"Connected" is printed when the `on_open` event handler is triggered.
The "Auth completed" statement was printed when the `on_message` event
handler was triggered and the message type was "auth".

If you want to play around further, keep the connection in your terminal and use
your web browser to navigate to Tutum. Redeploy one of your current services or
launch a new service (the tutum/hello-world service is an easy sample). Your
terminal should post a number of messages relating to the creation of a new
service and other updates.

##Monitoring your Tutum Stream client with Pagerduty

By the end of this tutorial, we'll have a service deployed on Tutum that is
connected to the Tutum Stream API and handling events as we desire. However,
we'll want to make sure our client is properly connected to the Stream API
at all times. After all, you can't send messages about your events if your
client is down.

To monitor our Stream client, we'll use [Pagerduty](http://www.pagerduty.com/).
Pagerduty allows you to get notifications if portions of your
infrastructure go down. You can send emails, text messages, or notifications
through mobile apps. You can trigger notifications using the Pagerduty
[Integration API](https://developer.pagerduty.com/documentation/integration/events).

In the repo for this project, I've written a function to post an event to
Pagerduty. Look at the `pagerduty_event()` function in `integrations/pagerduty.py`.
The important part of the function is as follows:

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

The function puts together some JSON and posts it to the Pagerduty endpoint. By
default, it sends a 'trigger' event to Pagerduty, which sends an alert to the
proper person. Note that you can also send a 'resolve' event to Pagerduty, which
indicates that a previously triggered issue has been resolved.

Let's see how this works in action. In the git repo, check out
`pagerduty-client.py`. It is the same as the `tutum-sample.py` script,
with two changes. First, the `on_close` handler has been changed:

    def on_close(ws):
        pagerduty_event(event_type='trigger', incident_key='tutum-stream', description='Tutum Stream connection closed.')
        print "### closed ###"

Once the WebSocket closes its connection, it sends a trigger event to Pagerduty.
This way, you'll be alerted when you are no longer connected to the Tutum Stream
API.

Similarly, look at the `on_open` handler:

    def on_open(ws):
        pagerduty_event(event_type='resolve', incident_key='tutum-stream', description='Tutum Stream connection open.')
        print "Connected"

This handler mirrors the `on_close` handler, as it sends a resolve event to Pagerduty.
If you previously sent a trigger event signaling that your Stream API client is down,
this will send a message that the problem has been fixed.

You could use this Pagerduty integration for all kinds of alerts. Another common use
case would be to use the `pagerduty_event` function in the `on_message` handler when
certain Services, Stacks, or Nodes are deleted. We'll investigate the `on_message`
handler more in the next section.

As a final note, if you want to use the `pagerduty_event()` function, you'll need to
set your PAGERDUTY_KEY as an environment variable. In your terminal, run:

    export PAGERDUTY_KEY=<your_Pagerduty_key>

##Posting Update Messages to Slack

Monitoring errors is responsible and all, but sometimes it's more fun to see the
good things your team is doing. This section will show you how to post messages to
[Slack](https://slack.com/) whenever you create a new Container on Tutum.

Again, let's look to the source code. Check out `integrations/slack.py`. There are
two functions:

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

The first function, `post_slack()`, is an implementation of the method to post
messages to Slack using the [Incoming Webhooks](https://api.slack.com/incoming-webhooks)
integration. To use this function, you'll need to register for a Webhook URL to
send POST requests. The second function, `generic_slack()`, is a simple wrapper
function around `post_slack`. It takes a message from the Tutum Stream API, and
it will post information about that update to your Slack channel.

Let's put this into action. Check out `client.py`. This will be our actual client
script that we end up deploying on Tutum. In particular, check out the last two
lines of the following:

    def on_message(ws, message):
        msg_as_JSON = json.loads(message)
        type = msg_as_JSON.get("type")
        if type:
            if type == "auth":
                print("Auth completed")
            elif type == "container":
                generic_slack(message)

This same checks to see if the `type` of event from the Tutum Stream is a "container"
event. If so, it posts a message to Slack using the `generic_slack` function.

Test it out yourself. In your terminal, set your SLACK_URL environment variable,
then run the client.

    export SLACK_URL=<your_Slack_url>
    python client.py

Navigate to the Tutum Dashboard with your browser. Deploy a new service or redeploy
an existing service. In your Slack channel, you should see a message like the following:

    Your container was created on Tutum!
    Check /api/v1/container/df3eb045-8bb9-46c1-ac59-a67ce0f4d875/ to see more details.

Congratulations! You've sent your first Tutum Stream event to Slack!

##Advanced Message Handling with Tutum Stream

The example above is nice, but it'd be nice to provide a little more info
about Tutum events. As discussed in part one of this tutorial, a message
from the Tutum Stream API includes a `resource_uri` and the resource_uri
of any `parents` of the event object. We can use these resource_uri's to
add additional information to our notifications.

The source code in `integrations/utilities.py` includes a helper function
called `get_resource()`. This function takes a resource_uri and returns
the text response from the Tutum API for that resource.

Look at the `on_message` handler in the `client.py` script. It has the
following code that is executed when the event type is "service":

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

This handler grabs the information about the Service's parent Stack. It
then posts a message to Slack about the status of the Stack with a
recently deployed Service.

This is a simple example, but you can use the `resource_uri` of both the
object and its parents to do some powerful stuff. For the ambitious, you
could parse the resource_uri of each and every event that is triggered and
post the information to ElasticSearch for later analysis.

##Deploying your Tutum Stream Client as a Tutum Service

So far, we've been running the Tutum Stream WebSockets client in our local
terminal. However, we'll want something that's always running to make sure
we're always tracking our Tutum events. To do this, we'll deploy the
WebSockets client as a service on Tutum in a Docker container.

In the git repo, I've provided a Dockerfile to get you started. It is based
on the [Alpine Linux image](https://github.com/gliderlabs/docker-alpine) from
the Gilder Labs team. Alpine Linux is a minimalist Linux distribution with
a pretty good package repository. The Dockerfile installs Python and Pip,
`pip installs` the required Python packages, and adds the code from your
repo.

To get the image on Tutum, run:

    docker build -t tutum.co/<username>/stream-client .
    docker push tutum.co/<username>/stream-client

In your Tutum browser, set up a Stack file with Stream:

    stream:
      image: 'tutum.co/<username>/tutum-stream:latest'
      environment:
       - PAGERDUTY_KEY=<your_Pagerduty_key>
       - SLACK_URL=<your_Slack_url>
       - TUTUM_TOKEN=<your_Tutum_token>
       - TUTUM_USERNAME=<your_Tutum_username>

Hit "Create and Deploy" and you're done! You'll be receiving Slack messages
and Pagerduty alerts with updates to your Tutum infrastructure!

##Conclusion

This tutorial has walked through integrating the Tutum Steam API into your
monitoring and communications systems. We learned how to send Pagerduty triggers
and Slack messages on specified Tutum events, as well as how to deploy a minimal
Docker image that monitors your Tutum Stream.

Please let me know of any questions or comments on this tutorial in the comment
box below. Interested in adding additional integrations? Feel free to fork the
repo for this tutorial and create a pull request with your new tool!
