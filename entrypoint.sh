#!/bin/sh
set -e
set -x
mod_wsgi-express start-server wsgi.py --port=80 --user www-data --group www-data --log-to-terminal
