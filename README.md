# Unbabel Fullstack Challenge

Hey :smile:

Welcome to our Fullstack Challenge repository. This README will guide you on how to participate in this challenge.

In case you are doing this to apply for our open positions for a Fullstack Developer make sure you first check the available jobs at [https://unbabel.com/jobs](https://unbabel.com/jobs)

Please fork this repo before you start working on the challenge. We will evaluate the code on the fork.

**FYI:** Please understand that this challenge is not decisive if you are applying to work at [Unbabel](https://unbabel.com/jobs). There are no right and wrong answers. This is just an opportunity for us both to work together and get to know each other in a more technical way.

## Challenge

We're going to build a very simple translation web app based on the Unbabel API.

You can find more info about the api at [https://developers.unbabel.com](https://developers.unbabel.com)

1) Request an API Key to your hiring manager or point of contact for the hiring process at Unbabel so you can use the API for this tutorial.  
2) Build a basic web app with a simple input field that takes an English (EN) input translates it to Spanish (ES).  
3) When a new translation is requested it should add to a list below the input field (showing one of three status: requested, pending or translated) - (note: always request human translation)   
4) The list should be dynamically ordered by the size of the translated messages   

#### Requirements
* Use Flask web framework
* Use Bootstrap
* Use PostgreSQL
* Create a scalable application. 
* Only use Unbabel's Translation API on sandbox mode
* Have tests


#### Notes
* Page load time shouldnt exceed 1 second


#### Resources
* Unbabel's API: http://developers.unbabel.com/


#### Booting this example
This example requires UNBABEL_API_KEY to be defined as an environment variable.
If you are using bash, you may just launch this server using:

`UNBABEL_API_KEY=some-key-you-have docker-compose -f server-compose.yaml up`

There's also `docker_start.sh` if you prefer.  
You may also start the server with gunicorn by running `start.sh`

You may also specify `UNBABEL_USERNAME` environment variable if you are not using the default one ("fullstack-challenge").

#### Known issues

* Page does not update automatically when a translation changes state.

A library in use (SocketIO) requires knowing how the server is running. I created the environment variable "SERVER_TYPE" (values either "threading" or "eventlet" (no quotes)) which allows you to select the mode which it will use. Supposedly "eventlet" works if running using "eventlet" but, sometimes, when using docker, the connections appear to be dropping (or even connection resets) outside user view.  
If the **web page does not update dynamically** when running in docker, try running without docker. If that doesn't work either, then try running without gunicorn and run the python program directly. It will use werzeug's dev server and should automatically set itself to "threading" mode.
