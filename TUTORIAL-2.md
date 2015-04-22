#Using the new Tutum Stream API
## Part Two: Practical Use Cases of the Tutum Stream API

##Introduction

Tutum recently introducted its new [Tutum Stream API](http://blog.tutum.co/2015/04/07/presenting-tutum-stream-api/).
This is a great new feature that allows you to use WebSockets to monitor
Events from your Tutum account. WebSockets are a big improvement over
long-polling and other conventional HTTP-based methods to stay informed
of changes to your application.

This is part two of a two-part tutorial will show you how to use the
Tutum Stream API. This part will show how to use the Tutum Stream
API for some common use cases, such as integrations with Slack, Pagerduty,
and others. It also shows how to deploy a service on Tutum that is always
connected to the Tutum Stream API to keep you apprised of changes to your
deployments.

To follow along with this tutorial, clone [this GitHub repo](https://github.com/alexdebrie/tutum-stream).
It has a sample `client.py` file as well as Python modules with code to
interact with Pagerduty and Slack. It even has a Dockerfile that you can use to
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
that Tutum showed in its [initial blog post]((http://blog.tutum.co/2015/04/07/presenting-tutum-stream-api/))
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
    
If you want to play around further, keep the connection in your terminal and use
your web browser to navigate to Tutum. Redeploy one of your current services or
launch a new service (the tutum/hello-world service is an easy sample). Your 
terminal should post a number of messages relating to the creation of a new 

##Conclusion

This tutorial has walked through integrating the Tutum Steam API into your
monitoring and communications systems. We learned how to send Pagerduty triggers
and Slack messages on specified Tutum events, as well as how to deploy a minimal
Docker image that monitors your Tutum Stream.

Please let me know of any questions or comments on this tutorial in the comment
box below. Interested in adding additional integrations? Feel free to fork the
repo for this tutorial and create a pull request with your new tool!
