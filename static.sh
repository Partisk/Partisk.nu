#!/bin/bash

rm -rf static/* && python3 manage.py compress && python3 manage.py collectstatic --noinput
