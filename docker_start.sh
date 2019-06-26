#!/usr/bin/env bash

SERVER_TYPE=eventlet gunicorn --worker-class eventlet -w 1 module:app
