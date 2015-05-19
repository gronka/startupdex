#!/bin/bash
#sudo pserve --daemon development.ini --user www-data
uwsgi --ini-paste uwsgi.ini --user taylor
