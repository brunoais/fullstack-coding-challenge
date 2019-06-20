#!/usr/bin/env bash
gunicorn --worker-class gevent -w 1 module:app
