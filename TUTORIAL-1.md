#Using the new Tutum Stream API
## Part One: WebSockets and Tutum Stream API Basics

##Introduction

Tutum recently introducted its new [Tutum Stream API](http://blog.tutum.co/2015/04/07/presenting-tutum-stream-api/).
This is a great new feature that allows you to use WebSockets to monitor
Events from your Tutum account. WebSockets are a big improvement over
long-polling and other conventional HTTP-based methods to stay informed
of changes to your application.

This is part one of a two-part tutorial will show you how to use the
Tutum Stream API. This part will cover the basics of WebSockets and
the Tutum Stream API. Part two[BL: INSERT LINK] will show how to use the Tutum Stream
API for some common use cases, such as integrations with Slack, Pagerduty,
and others.

##Basics of WebSockets

WebSockets are a new way to enable two-way communication with a remote
host. The websocket protocol is much more lightweight than typical HTTP,
as the usual HTTP headers are not needed. This can reduce message size
to a fraction of that required by HTTP and reduce latency.

###Polling, Long-Polling, and WebSockets

Before WebSockets, the typical way to check for updates from a remote host
(typically a REST API) was to use polling or long-polling. With polling,
the client pings the remote host at specified intervals to see if there
are any changes. Think of a kid on a long car ride asking "Are we there
yet?" every 5 minutes. The server (or parent, in our example) responds
immediately with a response: yes this information has changed, or no it is
still the same. This is not the most efficient method. It introduces a
lot of unnecessary requests, as many times the client will poll the remote
host and find out that nothing has changed. Further, any changes that do
occur may be delayed. If a client chooses to poll every minute, the
information it receives may be 59 seconds late. You can reduce this delay
by polling more frequently but that increases the load on the remote host.

Concerns about receiving out-of-date information can be reduced by using
long-polling. With long-polling, the client sends a request to the remote
host with a note to send the response only when there is new information or
once an expiration period has passed. The server keeps the request open until
new information is ready or until the request has expired. This allows the client
to receive updated information more quickly, but it increases the number of
open requests the remote host must handle. Further, it still includes a lot of
unnecessary header information that increases network load.

Using WebSockets improves on both of these prior methods. When establishing a
websocket connection, the client sends a typical HTTP request that asks
to upgrade to a websocket connection. If the remote host supports WebSockets,
the connection is upgraded. The connection is full-duplex, meaning both
client and server can send messages to each other at the same time. If the
remote host has an update, it can immediately send it to the client without
the overhead of HTTP headers. This significantly reduces the latency and
network load of updating data.

###Using WebSockets

To use WebSockets, you need to initialize a connection to the remote host with
a websocket client. In Python, the connection will look like the following:

    ws = websocket.WebSocketApp('wss://<websocket_url>',
     on_message = on_message,
     on_error = on_error,
     on_close = on_close,
     on_open = on_open)

The first variable passed to the client is the url of the remote websocket. The
remaining variables set up *event handlers* for the websocket client. The
websocket client fires event notifications when certain events happen during its
lifecycle. For example, when the websocket client connects to the remote host, it
will send the `open` event notification, which will trigger the `on_open` event
handler. Similarly, when the remote host sends a message, the client will send the
`message` event notification, which will trigger the `on_message` event handler.

You'll need to set up your event handlers for your websocket client. These are
functions that will be called with the associated event is fired. A sample
`on_message` event handler to print the contents of the message is below:

    def on_message(ws, message):
        print "I got a message: {}".format(message)

##The Tutum Stream API

Now that we've got the basics of WebSockets covered, let's explore how
the Tutum Stream API works.

###Message format

When using the Tutum Stream API, you will be most interested in receiving messages.
This will trigger the `on_message` event handler, and you can use the data to send
Slack notifications, Pagerduty triggers, or other actions.

You can read about the format of Tutum Event message [here](https://docs.tutum.co/v2/api/#tutum-events).
Basically, you will receive a JSON object with the following attributes:
`type`, `action`, `parents`, `resource_uri`, and `state`. By way of
example, here is one of the messages I received from the Tutum WebSocket
when I restarted a service (UUIDs are anonymized):

    {
        "state":"Starting",
        "parents":[
            "/api/v1/service/d0b1eb62-7662-4a81-8a10-d5a74b07811e/",
            "/api/v1/node/75d2f30f-ada7-4df5-ac49-c97aac3b8b7a/",
            "/api/v1/stack/f24bca18-e1dd-40aa-9b3c-064c0c26683e/",
            "/api/v1/nodecluster/99908d8c-027a-4124-a868-274db7f3e6ca/"
        ],
        "action":"create",
        "type":"container",
        "resource_uri":"/api/v1/container/fa159860-9048-4d1e-8655-6285fa9e3fa2/"
    }

When breaking this down, we can see that Tutum is *creating* (from the `action`
attribute), a *container* (from the `type` attribute), and it provides the
`resource_uri` of that container. It also provides a list of `parent` values.
I can use these values to find the objects that this container belongs to, such
as the particular Node or the Node Cluster, if I'm interested in the hardware,
or the Service or Stack, if I'm tracking that all my services are working.

###Using Parents or Resource URIs

When handling this Event, I may want to use of the `parents` or the `resource_uri`
to send acquire additional information. For example, when I discover that I created
a new container above, I may want to check the state of the Stack to which the
new container belongs. I can issue a `GET` request to the Stack endpoint, which
was `"/api/v1/stack/f24bca18-e1dd-40aa-9b3c-064c0c26683e/"` in the example above.
I'll get a response with the following information:

    {
        ...
        "state": "Partly running"
        "stack": "/api/v1/stack/f24bca18-e1dd-40aa-9b3c-064c0c26683e/",
        ...
    }

This would indicate that my Stack is only partially running and that there may be
a problem with my deployment. Based on this information, I may want to send a
Pagerduty alert to check out any problems with the Stack.

Note that this is only a small subset of the information I would receive from the
Stack endpoint. Check out Tutum's [Stack API documentation](https://docs.tutum.co/v2/api/?http#stack)
to see all of the attributes that will be returned.

##Conclusion

This tutorial has covered the basics of WebSockets and using a WebSocket client.
It then reviewed the structure of Tutum Event messages to get a feel for what
WebSocket messages you will receive from the Tutum Stream API. Check out
Part Two[BL: INSERT LINK] of this tutorial to get an idea of how to deploy your WebSocket client
as a Tutum service that sends notifications to Slack, Pagerduty, and more.
